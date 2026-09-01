"""Generate Magewire's static, Markdown-derived AI documentation outputs.

The file has two entry points so both build paths use the same implementation:

* Zensical invokes it as a command after ``zensical build``.
* Material for MkDocs loads it through the ``hooks`` configuration.

No generated HTML is read. The command reads the canonical Markdown navigation,
expands Magewire's small ``include()`` macro, and writes plain-text resources to
the already-generated site directory.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
from typing import Any, Iterable

import yaml


_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_INCLUDE_RE = re.compile(r"\{\{\s*(include\(.*?\))\s*\}\}")
_PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_]\w*)\s*\}\}")

_AI_GUARDRAILS = (
    "Magewire is inspired by server-driven frontend frameworks such as Laravel "
    "Livewire, but Magewire has its own Magento-specific API and behaviour. Do "
    "not assume Laravel Livewire APIs, directives, lifecycle hooks, or features "
    "exist in Magewire unless they are explicitly documented here. When this "
    "documentation and prior model knowledge conflict, prefer the Magewire "
    "documentation."
)


@dataclass(frozen=True)
class Page:
    source: str
    title: str
    summary: str
    url: str
    raw_url: str
    markdown: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Section:
    title: str
    slug: str
    sources: tuple[str, ...]


@dataclass(frozen=True)
class Project:
    site_name: str
    site_url: str
    summary: str
    documentation_version: str
    site_dir: Path


# State used only when Material for MkDocs imports this file as a hook.
_hook_pages: dict[str, Page] = {}
_hook_sections: list[Section] = []


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate llms.txt, llms-full.txt, and topic context bundles"
    )
    parser.add_argument("--config-file", default="mkdocs.yml", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    project, sections, pages = _load_sources(args.config_file, args.output_dir)
    outputs = _generate(project, sections, pages)
    print(
        f"Generated {len(outputs)} AI documentation files from "
        f"{len(pages)} Markdown pages"
    )


def _load_sources(
    config_file: Path, output_dir: Path | None
) -> tuple[Project, list[Section], dict[str, Page]]:
    config_file = config_file.resolve()
    with config_file.open(encoding="utf-8") as handle:
        # BaseLoader keeps custom MkDocs YAML tags inert. The generator only
        # needs strings, mappings, and lists from the project configuration.
        config = yaml.load(handle, Loader=yaml.BaseLoader)

    if not isinstance(config, dict):
        raise ValueError(f"Expected a mapping in {config_file}")

    root = config_file.parent
    docs_dir = (root / config.get("docs_dir", "docs")).resolve()
    site_dir = (
        output_dir.resolve()
        if output_dir is not None
        else (root / config.get("site_dir", "site")).resolve()
    )
    extra = config.get("extra") or {}
    ai_config = extra.get("ai_docs") or {}
    includes_config = extra.get("includes") or {}
    includes_dir = (root / includes_config.get("dir", "includes")).resolve()

    project = Project(
        site_name=_required(config, "site_name"),
        site_url=_required(config, "site_url").rstrip("/"),
        summary=_required(ai_config, "summary"),
        documentation_version=_required(ai_config, "documentation_version"),
        site_dir=site_dir,
    )
    sections = _parse_nav(config.get("nav") or [])
    if not sections:
        raise ValueError("The configured navigation contains no Markdown pages")

    use_directory_urls = str(config.get("use_directory_urls", "true")).lower() not in {
        "false",
        "no",
        "0",
    }
    pages: dict[str, Page] = {}
    for source in _unique(source for section in sections for source in section.sources):
        source_path = (docs_dir / source).resolve()
        if not source_path.is_relative_to(docs_dir):
            raise ValueError(f"Navigation path escapes docs_dir: {source}")
        if not source_path.is_file():
            raise FileNotFoundError(f"Navigation source does not exist: {source_path}")

        raw = source_path.read_text(encoding="utf-8")
        metadata, markdown = _split_front_matter(raw)
        markdown = _expand_includes(markdown, includes_dir)
        markdown = _strip_template_controls(markdown).strip()
        title = (
            str(metadata.get("title", "")).strip()
            or _extract_title(markdown)
            or _title_from_path(source)
        )
        if not _has_leading_h1(markdown):
            markdown = f"# {title}\n\n{markdown}"

        pages[source] = Page(
            source=f"docs/{source}",
            title=title,
            summary=_extract_summary(markdown),
            url=_page_url(source, use_directory_urls),
            raw_url=_raw_page_url(_page_url(source, use_directory_urls)),
            markdown=markdown.rstrip() + "\n",
            metadata=metadata,
        )

    _validate_pages(sections, pages)
    return project, sections, pages


def _parse_nav(nav: list[Any]) -> list[Section]:
    sections: list[Section] = []
    for item in nav:
        if isinstance(item, str):
            sources = tuple(_collect_nav_sources(item))
            if sources:
                title = _title_from_path(sources[0])
                sections.append(Section(title, _slugify(title), sources))
            continue

        if not isinstance(item, dict) or len(item) != 1:
            raise ValueError(f"Unsupported top-level navigation entry: {item!r}")
        title, children = next(iter(item.items()))
        sources = tuple(_collect_nav_sources(children))
        if sources:
            sections.append(Section(str(title), _slugify(str(title)), sources))

    slugs = [section.slug for section in sections]
    if len(slugs) != len(set(slugs)):
        raise ValueError("Top-level navigation produces duplicate AI topic slugs")
    return sections


def _collect_nav_sources(item: Any) -> Iterable[str]:
    if isinstance(item, str):
        if item.endswith(".md") and "://" not in item:
            yield PurePosixPath(item).as_posix()
        return
    if isinstance(item, list):
        for child in item:
            yield from _collect_nav_sources(child)
        return
    if isinstance(item, dict):
        for child in item.values():
            yield from _collect_nav_sources(child)


def _expand_includes(
    markdown: str, includes_dir: Path, stack: tuple[Path, ...] = ()
) -> str:
    includes_root = includes_dir.resolve()

    def replace(match: re.Match[str]) -> str:
        expression = ast.parse(match.group(1), mode="eval").body
        if (
            not isinstance(expression, ast.Call)
            or not isinstance(expression.func, ast.Name)
            or expression.func.id != "include"
            or len(expression.args) != 1
            or not isinstance(expression.args[0], ast.Constant)
            or not isinstance(expression.args[0].value, str)
        ):
            raise ValueError(f"Unsupported include expression: {match.group(0)}")

        include_path = (includes_root / expression.args[0].value).resolve()
        if not include_path.is_relative_to(includes_root):
            raise ValueError(f"Include path escapes includes directory: {include_path}")
        if include_path in stack:
            chain = " -> ".join(str(path) for path in (*stack, include_path))
            raise ValueError(f"Recursive include detected: {chain}")
        if not include_path.is_file():
            raise FileNotFoundError(f"Included Markdown file does not exist: {include_path}")

        values: dict[str, str] = {}
        for keyword in expression.keywords:
            if keyword.arg is None or not isinstance(keyword.value, ast.Constant):
                raise ValueError(f"Unsupported include argument: {match.group(0)}")
            values[keyword.arg] = str(keyword.value.value)

        content = include_path.read_text(encoding="utf-8")
        for key, value in values.items():
            content = content.replace(f"{{{{ {key} }}}}", value)
        unresolved = _PLACEHOLDER_RE.search(content)
        if unresolved:
            raise ValueError(
                f"Missing value for include placeholder {unresolved.group(1)!r} "
                f"in {include_path}"
            )
        return _expand_includes(content, includes_root, (*stack, include_path))

    return _INCLUDE_RE.sub(replace, markdown)


def _split_front_matter(markdown: str) -> tuple[dict[str, Any], str]:
    lines = markdown.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, markdown
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() in {"---", "..."}:
            raw_metadata = "".join(lines[1:index])
            metadata = yaml.safe_load(raw_metadata) or {}
            if not isinstance(metadata, dict):
                raise ValueError("Markdown front matter must be a mapping")
            return metadata, "".join(lines[index + 1 :])
    return {}, markdown


def _strip_template_controls(markdown: str) -> str:
    return markdown.replace("{% raw %}", "").replace("{% endraw %}", "")


def _page_url(source: str, use_directory_urls: bool) -> str:
    path = PurePosixPath(source)
    if not use_directory_urls:
        return path.with_suffix(".html").as_posix()
    if path.name == "index.md":
        return "" if path.parent == PurePosixPath(".") else f"{path.parent.as_posix()}/"
    return f"{path.with_suffix('').as_posix()}/"


def _raw_page_url(page_url: str) -> str:
    if not page_url:
        return "index.md"
    if page_url.endswith(".html"):
        return f"{page_url[:-5]}.md"
    if page_url.endswith("/"):
        return f"{page_url}index.md"
    return f"{page_url}.md"


def _generate(
    project: Project, sections: list[Section], pages: dict[str, Page]
) -> dict[Path, str]:
    outputs: dict[Path, str] = {
        project.site_dir / "llms.txt": _render_index(project, sections, pages),
        project.site_dir / "llms-full.txt": _render_full(project, sections, pages),
    }
    for section in sections:
        outputs[project.site_dir / "ai" / f"{section.slug}.txt"] = _render_topic(
            project, section, pages
        )
    for source in _unique(source for section in sections for source in section.sources):
        page = pages[source]
        raw_path = project.site_dir / page.raw_url
        if raw_path in outputs:
            raise ValueError(f"Raw Markdown output collides with AI resource: {raw_path}")
        outputs[raw_path] = page.markdown

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
    _validate_generated_outputs(project, sections, pages, outputs)
    return outputs


def _render_index(
    project: Project, sections: list[Section], pages: dict[str, Page]
) -> str:
    lines = _preamble(project, f"# {project.site_name}")
    lines.extend(
        [
            "## AI resources",
            "",
            f"- [Full documentation]({_absolute_url(project, 'llms-full.txt')}): "
            "Complete documentation context in navigation order.",
        ]
    )
    for section in sections:
        lines.append(
            f"- [{section.title} context]({_absolute_url(project, f'ai/{section.slug}.txt')}): "
            f"Complete context for the {section.title} section."
        )
    lines.append("")

    for section in sections:
        lines.extend([f"## {section.title}", ""])
        for source in section.sources:
            page = pages[source]
            link = f"[{page.title}]({_absolute_url(project, page.raw_url)})"
            lines.append(f"- {link}: {page.summary}" if page.summary else f"- {link}")
        lines.append("")
    return "\n".join(lines)


def _render_full(
    project: Project, sections: list[Section], pages: dict[str, Page]
) -> str:
    lines = _preamble(project, f"# {project.site_name} — Full Documentation")
    seen: set[str] = set()
    for section in sections:
        lines.extend(_section_separator(section.title))
        for source in section.sources:
            if source in seen:
                continue
            seen.add(source)
            lines.extend(_render_page(project, section.title, pages[source]))
    return "\n".join(lines)


def _render_topic(project: Project, section: Section, pages: dict[str, Page]) -> str:
    lines = _preamble(project, f"# {project.site_name} — {section.title}")
    lines.extend(["## Contents", ""])
    for source in section.sources:
        page = pages[source]
        link = f"[{page.title}]({_absolute_url(project, page.raw_url)})"
        lines.append(f"- {link}: {page.summary}" if page.summary else f"- {link}")
    lines.append("")
    lines.extend(_section_separator(section.title))
    for source in section.sources:
        lines.extend(_render_page(project, section.title, pages[source]))
    return "\n".join(lines)


def _preamble(project: Project, heading: str) -> list[str]:
    return [
        heading,
        "",
        f"> {project.summary}",
        "",
        f"Documentation version: {project.documentation_version}",
        f"Canonical documentation: {project.site_url}/",
        "",
        "**Important for AI and coding agents:**",
        "",
        _AI_GUARDRAILS,
        "",
    ]


def _section_separator(title: str) -> list[str]:
    return ["=" * 72, f"SECTION: {title.upper()}", "=" * 72, ""]


def _render_page(project: Project, section_title: str, page: Page) -> list[str]:
    lines = [
        "-" * 72,
        f"SOURCE DOCUMENT: {page.source}",
        f"SECTION: {section_title}",
        f"CANONICAL URL: {_absolute_url(project, page.url)}",
    ]
    meaningful_metadata = {
        key: value
        for key, value in page.metadata.items()
        if key in {"title", "description", "date", "tags", "status"}
    }
    for key, value in meaningful_metadata.items():
        lines.append(f"{key.upper()}: {value}")
    lines.extend(["-" * 72, "", page.markdown.rstrip(), ""])
    return lines


def _absolute_url(project: Project, relative: str) -> str:
    return f"{project.site_url}/{relative.lstrip('/')}"


def _validate_pages(sections: list[Section], pages: dict[str, Page]) -> None:
    expected = {source for section in sections for source in section.sources}
    missing = expected - pages.keys()
    if missing:
        raise ValueError(f"Missing AI documentation pages: {sorted(missing)}")
    for source in expected:
        page = pages[source]
        if _INCLUDE_RE.search(page.markdown):
            raise ValueError(f"Unexpanded include in {page.source}")
        if "{% raw %}" in page.markdown or "{% endraw %}" in page.markdown:
            raise ValueError(f"Unexpanded template control in {page.source}")


def _validate_generated_outputs(
    project: Project,
    sections: list[Section],
    pages: dict[str, Page],
    outputs: dict[Path, str],
) -> None:
    aggregate_paths = {
        project.site_dir / "llms.txt",
        project.site_dir / "llms-full.txt",
        *(
            project.site_dir / "ai" / f"{section.slug}.txt"
            for section in sections
        ),
    }
    for path, content in outputs.items():
        if not content.strip() or not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"AI documentation output is empty or missing: {path}")
        if path in aggregate_paths and _AI_GUARDRAILS not in content:
            raise ValueError(f"AI guardrails are missing from: {path}")

    navigated_sources = {
        source for section in sections for source in section.sources
    }
    for source in navigated_sources:
        page = pages[source]
        relative = page.url.strip("/")
        if not relative:
            relative = "index.html"
        elif page.url.endswith("/"):
            relative = f"{relative}/index.html"
        target = project.site_dir / relative
        if not target.is_file():
            raise ValueError(
                f"Canonical AI index target does not exist in the built site: {target}"
            )
        raw_target = project.site_dir / page.raw_url
        if outputs.get(raw_target) != page.markdown:
            raise ValueError(f"Raw Markdown output does not match its source: {raw_target}")

    full = outputs[project.site_dir / "llms-full.txt"]
    if full.count("SOURCE DOCUMENT:") != len(navigated_sources):
        raise ValueError("llms-full.txt does not contain every navigated source document")
    for section in sections:
        topic = outputs[project.site_dir / "ai" / f"{section.slug}.txt"]
        if topic.count("SOURCE DOCUMENT:") != len(section.sources):
            raise ValueError(f"Topic bundle is incomplete: {section.slug}")


def _required(mapping: dict[str, Any], key: str) -> str:
    value = str(mapping.get(key, "")).strip()
    if not value:
        raise ValueError(f"Missing required configuration value: {key}")
    return value


def _extract_title(markdown: str) -> str:
    match = _H1_RE.search(markdown)
    return match.group(1).strip() if match else ""


def _has_leading_h1(markdown: str) -> bool:
    match = _H1_RE.search(markdown)
    return bool(match and not markdown[: match.start()].strip())


def _title_from_path(source: str) -> str:
    return PurePosixPath(source).stem.replace("-", " ").title()


def _extract_summary(markdown: str) -> str:
    match = _H1_RE.search(markdown)
    body = markdown[match.end() :] if match else markdown
    paragraph: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if _is_skippable(raw, line):
            if paragraph:
                break
            continue
        paragraph.append(line)

    text = _demark(" ".join(paragraph))
    if not text:
        return ""
    sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    return sentence[:197].rstrip() + "..." if len(sentence) > 200 else sentence


def _is_skippable(raw: str, line: str) -> bool:
    if not line or raw[:1] in (" ", "\t"):
        return True
    if line.startswith(("#", "!!!", "???", ">", "```", "|", "<!--", "--8<")):
        return True
    if line.startswith(("- ", "* ", "+ ")) or re.match(r"^\d+\.\s", line):
        return True
    return bool(re.match(r"^\[[^\]]*\]:\s", line))


def _demark(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"[`*_~]", "", text).strip()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError(f"Unable to create topic slug from {value!r}")
    return slug


def _unique(values: Iterable[str]) -> Iterable[str]:
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            yield value


# Material for MkDocs hook compatibility ---------------------------------


def _gather_hook_pages(item: Any, sources: list[str]) -> None:
    if item.is_page:
        if item.file is not None and item.file.src_uri:
            sources.append(item.file.src_uri)
    elif item.is_section:
        for child in item.children:
            _gather_hook_pages(child, sources)


def on_nav(nav: Any, config: Any, files: Any) -> Any:  # noqa: ARG001
    _hook_pages.clear()
    _hook_sections.clear()
    for item in nav.items:
        sources: list[str] = []
        if item.is_section:
            _gather_hook_pages(item, sources)
            title = item.title
        elif item.is_page and item.file is not None:
            sources.append(item.file.src_uri)
            title = item.title or _title_from_path(item.file.src_uri)
        else:
            continue
        if sources:
            _hook_sections.append(Section(title, _slugify(title), tuple(sources)))
    return nav


def on_page_markdown(
    markdown: str, page: Any, config: Any, files: Any  # noqa: ARG001
) -> str:
    source = page.file.src_uri
    ai_markdown = _strip_template_controls(markdown).strip()
    title = _extract_title(ai_markdown) or page.title or _title_from_path(source)
    if not _has_leading_h1(ai_markdown):
        ai_markdown = f"# {title}\n\n{ai_markdown}"
    _hook_pages[source] = Page(
        source=f"docs/{source}",
        title=title,
        summary=_extract_summary(ai_markdown),
        url=page.url,
        raw_url=_raw_page_url(page.url),
        markdown=ai_markdown.rstrip() + "\n",
        metadata=dict(page.meta or {}),
    )
    return markdown


def on_post_build(config: Any) -> None:
    extra = config.get("extra") or {}
    ai_config = extra.get("ai_docs") or {}
    project = Project(
        site_name=config.get("site_name") or "Documentation",
        site_url=(config.get("site_url") or "").rstrip("/"),
        summary=_required(ai_config, "summary"),
        documentation_version=_required(ai_config, "documentation_version"),
        site_dir=Path(config["site_dir"]),
    )
    _validate_pages(_hook_sections, _hook_pages)
    _generate(project, _hook_sections, _hook_pages)


if __name__ == "__main__":
    main()
