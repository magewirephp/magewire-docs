"""
MkDocs hook that generates `/llms.txt` and `/llms-full.txt` at build time.

- llms.txt        A curated, link-based index (the llmstxt.org standard): an H1
                  title, a summary blockquote, then one H2 per top-level nav
                  section with a bullet per page (`[title](url): summary`).
- llms-full.txt   The entire documentation inlined into a single file, in nav
                  order, for LLMs that want the full corpus in one fetch.

Both files are written into the built `site/` directory so they are served at
the site root (e.g. https://docs.magewirephp.nl/llms.txt).

Implemented as a native MkDocs hook so no extra pip dependency is needed in CI.
Hook events run *after* plugin events for the same hook, so by the time
`on_page_markdown` fires here the macros plugin has already expanded every
`{{ include(...) }}` — the captured markdown is fully resolved.
"""

from __future__ import annotations

import os
import re

# Captured during the build. Keyed by a page's source path (src_uri).
_pages: dict[str, dict] = {}
# Ordered nav structure: list of (section_title, [src_uri, ...]).
_sections: list[tuple[str, list[str]]] = []

# A short, factual one-liner describing the project for the llms.txt header.
_CONTEXT = (
    "Magewire is a reactive, full-stack component framework for Magento 2, "
    "inspired by Laravel Livewire. It lets developers build dynamic interfaces "
    "in PHP and PHTML without writing custom JavaScript."
)


def _gather_pages(item, acc: list[str]) -> None:
    """Recursively collect page source paths under a nav item, in order."""
    if item.is_page:
        if item.file is not None and item.file.src_uri:
            acc.append(item.file.src_uri)
    elif item.is_section:
        for child in item.children:
            _gather_pages(child, acc)
    # Links (external) are intentionally skipped.


def on_nav(nav, config, files):
    """Capture the ordered nav structure (titles + page order)."""
    _sections.clear()
    for item in nav.items:
        if item.is_section:
            acc: list[str] = []
            _gather_pages(item, acc)
            if acc:
                _sections.append((item.title, acc))
        elif item.is_page and item.file is not None:
            # A loose top-level page without a wrapping section.
            _sections.append((item.title or item.file.src_uri, [item.file.src_uri]))
    return nav


def on_page_markdown(markdown, page, config, files):
    """Capture the fully-resolved markdown + metadata for each page."""
    _pages[page.file.src_uri] = {
        "title": _extract_title(markdown) or page.title or page.file.src_uri,
        "summary": _extract_summary(markdown),
        "url": page.url,
        "markdown": markdown,
    }
    return markdown


def on_post_build(config):
    """Write llms.txt and llms-full.txt into the built site directory."""
    site_dir = config["site_dir"]
    site_url = (config.get("site_url") or "").rstrip("/")
    site_name = config.get("site_name") or "Documentation"
    site_description = config.get("site_description") or ""

    def abs_url(rel: str) -> str:
        return f"{site_url}/{rel.lstrip('/')}" if site_url else rel

    # ---- llms.txt (curated index) ----------------------------------------
    index_lines: list[str] = [f"# {site_name}", ""]
    if site_description:
        index_lines += [f"> {site_description}", ""]
    index_lines += [_CONTEXT, ""]
    if site_url:
        index_lines += [
            f"The complete documentation inlined into a single file is available "
            f"at [{site_url}/llms-full.txt]({site_url}/llms-full.txt).",
            "",
        ]

    for title, src_uris in _sections:
        index_lines.append(f"## {title}")
        for src_uri in src_uris:
            page = _pages.get(src_uri)
            if page is None:
                continue
            link = f"[{page['title']}]({abs_url(page['url'])})"
            if page["summary"]:
                index_lines.append(f"- {link}: {page['summary']}")
            else:
                index_lines.append(f"- {link}")
        index_lines.append("")

    _write(os.path.join(site_dir, "llms.txt"), "\n".join(index_lines).rstrip() + "\n")

    # ---- llms-full.txt (full corpus) -------------------------------------
    full_lines: list[str] = [f"# {site_name} — Full Documentation", ""]
    if site_description:
        full_lines += [f"> {site_description}", ""]
    if site_url:
        full_lines += [f"Source: {site_url}", ""]
    full_lines.append("")

    seen: set[str] = set()
    for _title, src_uris in _sections:
        for src_uri in src_uris:
            if src_uri in seen:
                continue
            seen.add(src_uri)
            page = _pages.get(src_uri)
            if page is None:
                continue
            full_lines.append("---")
            full_lines.append("")
            full_lines.append(f"# {page['title']}")
            full_lines.append("")
            if site_url:
                full_lines.append(f"Source: {abs_url(page['url'])}")
                full_lines.append("")
            full_lines.append(_strip_leading_h1(page["markdown"]).strip())
            full_lines.append("")

    _write(os.path.join(site_dir, "llms-full.txt"), "\n".join(full_lines).rstrip() + "\n")


# --- helpers --------------------------------------------------------------

_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def _extract_title(markdown: str) -> str | None:
    match = _H1_RE.search(markdown)
    return match.group(1).strip() if match else None


def _strip_leading_h1(markdown: str) -> str:
    """Drop the first H1 (we render the title ourselves in llms-full.txt)."""
    match = _H1_RE.search(markdown)
    if match and markdown[: match.start()].strip() == "":
        return markdown[: match.start()] + markdown[match.end() :]
    return markdown


def _extract_summary(markdown: str) -> str:
    """First meaningful prose sentence after the H1, lightly de-marked."""
    body = _strip_leading_h1(markdown)
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Skip indented content — admonition bodies, code blocks, list/table
        # continuations — so the summary is genuine top-level intro prose.
        if raw[:1] in (" ", "\t"):
            continue
        # Skip headings, admonitions, blockquotes, code fences, list/table markup,
        # html comments and leftover macro/snippet syntax.
        if line.startswith(("#", "!!!", "???", ">", "```", "|", "<!--", "{{", "--8<")):
            continue
        if line.startswith(("- ", "* ", "+ ")) or re.match(r"^\d+\.\s", line):
            continue
        # Skip link-reference definitions and `[//]: # (...)` comment lines.
        if re.match(r"^\[[^\]]*\]:\s", line):
            continue
        text = _demark(line)
        if not text:
            continue
        # Cut to the first sentence; cap length so the index stays scannable.
        sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
        if len(sentence) > 200:
            sentence = sentence[:197].rstrip() + "..."
        return sentence
    return ""


def _demark(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [label](url) -> label
    text = re.sub(r"[`*_~]", "", text)  # inline code / emphasis markers
    return text.strip()


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)