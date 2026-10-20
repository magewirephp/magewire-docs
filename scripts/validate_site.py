"""Validate the complete static documentation artifact before publication.

The validator treats ``mkdocs.yml`` navigation as the source of truth. It checks
the human HTML, committed AI snapshots, search index, important legacy URLs,
and local links without making network requests or refreshing the snapshots.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit

import yaml


_IMPORTANT_URLS = (
    "index.html",
    "pages/getting-started/basics.html",
    "pages/essentials/components.html",
    "pages/html-directives/wire-click.html",
    "pages/concepts/fragments.html",
    "pages/admin/index.html",
    "pages/advanced/security.html",
    "pages/advanced/architecture/index.html",
)
_MARKDOWN_LINK_RE = re.compile(
    r"(?<!!)\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)"
)
_MARKDOWN_IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)"
)
_FENCED_BLOCK_RE = re.compile(
    r"^\s*(`{3,}|~{3,}).*?^\s*\1\s*$", re.MULTILINE | re.DOTALL
)
_INLINE_CODE_RE = re.compile(r"(`+)(.*?)\1", re.DOTALL)
_SKIPPED_SCHEMES = {"data", "javascript", "mailto", "tel"}
_AI_SNAPSHOTS = {PurePosixPath("llms.txt"), PurePosixPath("llms-full.txt")}


@dataclass(frozen=True)
class Reference:
    source: PurePosixPath
    target: str
    kind: str


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()
        self.links: list[tuple[str, str]] = []
        self.runtime_assets: list[tuple[str, str, str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        values = {name: value for name, value in attrs if value is not None}
        for name in ("id", "name"):
            if values.get(name):
                self.anchors.add(values[name])
        for name in ("href", "src"):
            if values.get(name):
                self.links.append((name, values[name]))
        if values.get("src"):
            self.runtime_assets.append((tag, "src", values["src"]))
        rel = set(values.get("rel", "").lower().split())
        if values.get("href") and rel.intersection(
            {
                "dns-prefetch",
                "icon",
                "manifest",
                "modulepreload",
                "preconnect",
                "preload",
                "stylesheet",
            }
        ):
            self.runtime_assets.append((tag, "href", values["href"]))

    handle_startendtag = handle_starttag


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the generated documentation site")
    parser.add_argument("--config-file", default="mkdocs.yml", type=Path)
    parser.add_argument("--site-dir", default="site", type=Path)
    args = parser.parse_args()

    site_dir = args.site_dir.resolve()
    site_url, docs_dir, expected_html = _load_site_layout(args.config_file)
    errors: list[str] = []

    _check_required_outputs(site_dir, docs_dir, expected_html, errors)
    html_documents = _parse_html_documents(site_dir, errors)
    _check_runtime_assets(html_documents, site_url, errors)
    html_reference_count = _check_html_links(
        site_dir, html_documents, site_url, errors
    )
    snapshot_reference_count = _check_snapshot_links(
        site_dir, html_documents, site_url, errors
    )
    search_count = _check_search(site_dir, html_documents, site_url, errors)

    if errors:
        print(f"Site validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(
        f"Validated {len(expected_html)} navigated pages, {len(html_documents)} HTML files, "
        f"{html_reference_count} HTML references, {snapshot_reference_count} "
        f"AI snapshot references, {search_count} search entries, and "
        "2 committed AI snapshot routes; "
        "no third-party runtime assets found"
    )


def _load_site_layout(config_file: Path) -> tuple[str, Path, set[PurePosixPath]]:
    config_file = config_file.resolve()
    # Keep MkDocs-specific YAML tags inert; only strings, lists, and mappings
    # are needed to derive the expected published page paths.
    config = yaml.load(config_file.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    site_url = config["site_url"].rstrip("/")
    docs_dir = (config_file.parent / config.get("docs_dir", "docs")).resolve()
    directory_urls = str(config.get("use_directory_urls", "true")).lower() not in {
        "false", "no", "0"
    }

    def collect(item):
        if isinstance(item, str):
            if item.endswith(".md") and "://" not in item:
                path = PurePosixPath(item)
                if directory_urls and path.name != "index.md":
                    yield path.with_suffix("") / "index.html"
                else:
                    yield path.with_suffix(".html")
        elif isinstance(item, list):
            for child in item:
                yield from collect(child)
        elif isinstance(item, dict):
            for child in item.values():
                yield from collect(child)

    expected_html = set(collect(config.get("nav", [])))
    if not expected_html:
        raise ValueError("The configured navigation contains no Markdown pages")
    return site_url, docs_dir, expected_html


def _check_required_outputs(
    site_dir: Path,
    docs_dir: Path,
    expected_html: set[PurePosixPath],
    errors: list[str],
) -> None:
    required = expected_html | _AI_SNAPSHOTS
    for relative in sorted(required):
        path = site_dir / relative
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"required output is missing or empty: {relative}")

    for path in sorted(site_dir.rglob("*.md")):
        errors.append(f"unexpected raw Markdown export: {path.relative_to(site_dir)}")
    for path in sorted((site_dir / "ai").glob("*.txt")):
        errors.append(f"unexpected AI topic export: {path.relative_to(site_dir)}")

    cname = site_dir / "CNAME"
    if not cname.is_file() or cname.read_text(encoding="utf-8").strip() != "docs.magewirephp.nl":
        errors.append("CNAME is missing or does not contain docs.magewirephp.nl")

    for relative in _IMPORTANT_URLS:
        if not (site_dir / relative).is_file():
            errors.append(f"important existing URL has no output file: /{relative}")

    for relative in sorted(_AI_SNAPSHOTS):
        path = site_dir / relative
        if not path.is_file():
            continue
        source = docs_dir / relative
        try:
            content = path.read_text(encoding="utf-8")
            if path.read_bytes() != source.read_bytes():
                errors.append(f"AI snapshot route differs from committed docs/{relative}")
        except (OSError, UnicodeError) as exception:
            errors.append(f"cannot read AI snapshot {relative}: {exception}")
            continue
        if not content.startswith("# "):
            errors.append(f"AI snapshot must start with a Markdown H1: {relative}")
        if not re.search(r"^Last refreshed: \d{4}-\d{2}-\d{2}$", content, re.MULTILINE):
            errors.append(f"AI snapshot has no refresh date: {relative}")


def _parse_html_documents(
    site_dir: Path, errors: list[str]
) -> dict[PurePosixPath, DocumentParser]:
    documents: dict[PurePosixPath, DocumentParser] = {}
    for path in sorted(site_dir.rglob("*.html")):
        relative = PurePosixPath(path.relative_to(site_dir).as_posix())
        parser = DocumentParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exception:
            errors.append(f"cannot parse HTML file {relative}: {exception}")
            continue
        documents[relative] = parser
    return documents


def _check_html_links(
    site_dir: Path,
    documents: dict[PurePosixPath, DocumentParser],
    site_url: str,
    errors: list[str],
) -> int:
    references: list[Reference] = []
    for source, document in documents.items():
        for kind, target in document.links:
            # Zensical 0.0.57 generates this one invalid skip link in its 404
            # page. It is outside authored documentation and tracked in the
            # migration notes as an upstream compatibility issue.
            if source == PurePosixPath("404.html") and target == "#__skip":
                continue
            references.append(Reference(source, target, f"HTML {kind}"))

    for reference in references:
        _check_reference(site_dir, documents, site_url, reference, errors)
    return len(references)


def _check_runtime_assets(
    documents: dict[PurePosixPath, DocumentParser],
    site_url: str,
    errors: list[str],
) -> None:
    site_host = urlsplit(site_url).netloc.lower()
    for source, document in documents.items():
        for tag, attribute, target in document.runtime_assets:
            parsed = urlsplit(unescape(target.strip()))
            if parsed.scheme.lower() not in {"http", "https"} and not target.startswith(
                "//"
            ):
                continue
            if parsed.netloc.lower() == site_host:
                continue
            errors.append(
                f"third-party runtime asset in {source}: "
                f"<{tag}> {attribute}={target}"
            )


def _check_snapshot_links(
    site_dir: Path,
    documents: dict[PurePosixPath, DocumentParser],
    site_url: str,
    errors: list[str],
) -> int:
    references: list[Reference] = []
    for source in sorted(_AI_SNAPSHOTS):
        path = site_dir / source
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        content = _INLINE_CODE_RE.sub("", _FENCED_BLOCK_RE.sub("", content))
        for kind, pattern in (
            ("Markdown link", _MARKDOWN_LINK_RE),
            ("Markdown image", _MARKDOWN_IMAGE_RE),
        ):
            for match in pattern.finditer(content):
                references.append(
                    Reference(source, unescape(match.group(1) or match.group(2)), kind)
                )

        html = DocumentParser()
        html.feed(content)
        for kind, target in html.links:
            references.append(Reference(source, target, f"raw HTML {kind}"))

    for reference in references:
        _check_reference(site_dir, documents, site_url, reference, errors)
    return len(references)


def _check_search(
    site_dir: Path,
    documents: dict[PurePosixPath, DocumentParser],
    site_url: str,
    errors: list[str],
) -> int:
    candidates = (
        (site_dir / "search.json", "items"),
        (site_dir / "search" / "search_index.json", "docs"),
    )
    selected = next(((path, key) for path, key in candidates if path.is_file()), None)
    if selected is None:
        errors.append("search index is missing")
        return 0
    path, item_key = selected
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as exception:
        errors.append(f"{path.relative_to(site_dir)} is invalid: {exception}")
        return 0

    items = payload.get(item_key) if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        errors.append(f"{path.relative_to(site_dir)} contains no search items")
        return 0
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not str(item.get("title", "")).strip():
            errors.append(f"search item {index} has no title")
            continue
        location = str(item.get("location", "")).strip()
        if not location:
            errors.append(f"search item {index} has no location")
            continue
        _check_reference(
            site_dir,
            documents,
            site_url,
            Reference(
                PurePosixPath("index.html"),
                f"/{location.lstrip('/')}",
                "search location",
            ),
            errors,
        )
    return len(items)


def _check_reference(
    site_dir: Path,
    documents: dict[PurePosixPath, DocumentParser],
    site_url: str,
    reference: Reference,
    errors: list[str],
) -> None:
    resolved = _resolve_reference(reference, site_url)
    if resolved is None:
        return
    target, fragment = resolved
    if target == PurePosixPath("..") or target.as_posix().startswith("../"):
        errors.append(
            f"{reference.kind} in {reference.source} escapes the site root: "
            f"{reference.target}"
        )
        return
    path = site_dir / target
    if not path.is_file():
        errors.append(
            f"{reference.kind} in {reference.source} points to missing {target}: "
            f"{reference.target}"
        )
        return
    if not fragment:
        return

    anchor_document = target
    if target.suffix == ".md":
        anchor_document = target.with_suffix(".html")
    document = documents.get(anchor_document)
    if document is not None and unquote(fragment) not in document.anchors:
        errors.append(
            f"{reference.kind} in {reference.source} points to missing anchor "
            f"{target}#{fragment}"
        )


def _resolve_reference(
    reference: Reference, site_url: str
) -> tuple[PurePosixPath, str] | None:
    value = unescape(reference.target.strip())
    parsed = urlsplit(value)
    site = urlsplit(site_url)
    if parsed.scheme.lower() in _SKIPPED_SCHEMES or value.startswith("//"):
        return None
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in {"http", "https"} or parsed.netloc != site.netloc:
            return None
        raw_path = unquote(parsed.path)
    else:
        raw_path = unquote(parsed.path)

    if raw_path.startswith("/"):
        relative = raw_path.lstrip("/")
    elif raw_path:
        relative = posixpath.normpath(
            posixpath.join(reference.source.parent.as_posix(), raw_path)
        )
    else:
        relative = reference.source.as_posix()

    if relative == ".." or relative.startswith("../"):
        return PurePosixPath(relative), parsed.fragment
    if raw_path.endswith("/"):
        relative = (
            "index.html"
            if not relative or relative == "."
            else f"{relative.rstrip('/')}/index.html"
        )
    elif not relative or relative == ".":
        relative = "index.html"
    return PurePosixPath(relative), parsed.fragment


if __name__ == "__main__":
    main()
