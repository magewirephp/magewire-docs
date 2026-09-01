"""Build Zensical-compatible blog pages from the canonical post Markdown.

Zensical 0.0.57 does not implement Material for MkDocs' blog plugin. This
adapter keeps ``docs/**/posts/*.md`` as the source of truth and creates an
ignored staging tree with the same routes Material published. The staged
Markdown is then rendered by Zensical like every other documentation page.

Run ``prepare`` before Zensical and ``finalize`` immediately after it. The
finalize step adds generated, unlisted blog routes to Zensical's sitemap and
checks that no source-path post URLs leaked into the artifact.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from html import escape
import math
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import unicodedata
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ElementTree

import yaml


_SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
_REDIRECT_MARKER = "<!-- magewire-blog-redirect -->"
_LINK_TARGET_RE = re.compile(
    r"(?P<prefix>!?\[[^\]]*\]\(\s*)(?P<angle><)?"
    r"(?P<target>[^>\s)]+)(?P<close>>)?"
)
_NUMBER_SUFFIX_RE = re.compile(r"\s+#\d+\s*$")
_WORD_RE = re.compile(r"\b[\w'’]+\b", re.UNICODE)
_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


@dataclass(frozen=True)
class Collection:
    source_dir: PurePosixPath
    route_dir: PurePosixPath
    dated_routes: bool
    taxonomy: str | None


@dataclass(frozen=True)
class Post:
    source: PurePosixPath
    title: str
    published: date
    authors: tuple[str, ...]
    taxonomy_values: tuple[str, ...]
    metadata: dict[str, object]
    body: str
    route: PurePosixPath
    heading_anchor: str


_COLLECTIONS = (
    Collection(PurePosixPath("blogs"), PurePosixPath("blogs"), True, None),
    Collection(
        PurePosixPath("personal"),
        PurePosixPath("personal"),
        False,
        "categories",
    ),
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare and finalize the Zensical blog compatibility build"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--docs-dir", default="docs", type=Path)
    prepare.add_argument("--output-dir", default=".build/docs", type=Path)

    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--docs-dir", default="docs", type=Path)
    finalize.add_argument("--site-dir", default="site", type=Path)
    finalize.add_argument(
        "--site-url", default="https://docs.magewirephp.nl", type=str
    )

    args = parser.parse_args()
    if args.command == "prepare":
        _prepare(args.docs_dir, args.output_dir)
    else:
        _finalize(args.docs_dir, args.site_dir, args.site_url)


def _prepare(docs_dir: Path, output_dir: Path) -> None:
    docs_dir = docs_dir.resolve()
    output_dir = output_dir.resolve()
    if not docs_dir.is_dir():
        raise SystemExit(f"Canonical docs directory does not exist: {docs_dir}")
    build_root = docs_dir.parent / ".build"
    if output_dir == build_root or not output_dir.is_relative_to(build_root):
        raise SystemExit(
            f"Staging directory must be a child of the build root: {build_root}"
        )

    collections = _load_collections(docs_dir)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(docs_dir, output_dir)

    generated = 0
    for collection, posts, authors in collections:
        staged_collection = output_dir / collection.source_dir
        staged_posts = staged_collection / "posts"
        if staged_posts.exists():
            shutil.rmtree(staged_posts)
        authors_file = staged_collection / ".authors.yml"
        if authors_file.exists():
            authors_file.unlink()

        canonical_index = docs_dir / collection.source_dir / "index.md"
        index_preamble = _body(canonical_index.read_text(encoding="utf-8"))[1]
        browse_links = _browse_links(collection, posts)
        _write(
            staged_collection / "index.md",
            _render_listing(
                f"{index_preamble.rstrip()}\n\n{browse_links}", posts, authors
            ),
        )

        for post in posts:
            _write(output_dir / post.route, _render_post(post, authors))
            generated += 1

        for year in sorted({post.published.year for post in posts}, reverse=True):
            yearly = tuple(post for post in posts if post.published.year == year)
            _write(
                staged_collection / "archive" / f"{year}.md",
                _render_listing(f"# {year}\n", yearly, authors),
            )
            generated += 1

        if collection.taxonomy:
            values = sorted(
                {value for post in posts for value in post.taxonomy_values},
                key=str.casefold,
            )
            for value in values:
                selected = tuple(
                    post for post in posts if value in post.taxonomy_values
                )
                _write(
                    staged_collection
                    / "category"
                    / f"{_heading_slug(value)}.md",
                    _render_listing(f"# {value}\n", selected, authors),
                )
                generated += 1

    post_count = sum(len(posts) for _, posts, _ in collections)
    print(
        f"Prepared {post_count} canonical posts and {generated - post_count} "
        f"archive/category pages in {output_dir}"
    )


def _finalize(docs_dir: Path, site_dir: Path, site_url: str) -> None:
    docs_dir = docs_dir.resolve()
    site_dir = site_dir.resolve()
    collections = _load_collections(docs_dir)
    routes: set[PurePosixPath] = set()
    redirects: dict[PurePosixPath, PurePosixPath] = {}
    for collection, posts, _authors in collections:
        routes.add(collection.route_dir / "index.html")
        routes.update(post.route.with_suffix(".html") for post in posts)
        redirects.update(
            {
                post.source.with_suffix(".html"): post.route.with_suffix(".html")
                for post in posts
            }
        )
        routes.update(
            collection.route_dir / "archive" / f"{year}.html"
            for year in {post.published.year for post in posts}
        )
        if collection.taxonomy:
            routes.update(
                collection.route_dir / "category" / f"{_heading_slug(value)}.html"
                for post in posts
                for value in post.taxonomy_values
            )

    missing = sorted(route for route in routes if not (site_dir / route).is_file())
    if missing:
        formatted = "\n".join(f"- /{route}" for route in missing)
        raise SystemExit(f"Generated blog routes are missing:\n{formatted}")

    for source, target in sorted(redirects.items()):
        path = site_dir / source
        if path.exists() and _REDIRECT_MARKER not in path.read_text(encoding="utf-8"):
            raise SystemExit(
                f"Zensical emitted duplicate blog content at /{source.as_posix()}"
            )
        _write(path, _redirect_html(site_url, target))

    sitemap = site_dir / "sitemap.xml"
    if not sitemap.is_file():
        raise SystemExit(f"Sitemap does not exist: {sitemap}")
    try:
        tree = ElementTree.parse(sitemap)
    except ElementTree.ParseError as exception:
        raise SystemExit(f"Cannot parse {sitemap}: {exception}") from exception

    root = tree.getroot()
    namespace = f"{{{_SITEMAP_NAMESPACE}}}"
    prefix = f"{site_url.rstrip('/')}/"
    existing = {
        location.text
        for location in root.findall(f"{namespace}url/{namespace}loc")
        if location.text
    }
    added = 0
    for route in sorted(routes):
        location = f"{prefix}{route.as_posix()}"
        if location in existing:
            continue
        url = ElementTree.SubElement(root, f"{namespace}url")
        ElementTree.SubElement(url, f"{namespace}loc").text = location
        added += 1

    ElementTree.register_namespace("", _SITEMAP_NAMESPACE)
    ElementTree.indent(tree, space="  ")
    tree.write(sitemap, encoding="UTF-8", xml_declaration=True)
    print(
        f"Verified {len(routes)} blog routes, wrote {len(redirects)} redirects, "
        f"and added {added} sitemap entries"
    )


def _load_collections(
    docs_dir: Path,
) -> list[tuple[Collection, tuple[Post, ...], dict[str, str]]]:
    loaded: list[tuple[Collection, tuple[Post, ...], dict[str, str]]] = []
    for collection in _COLLECTIONS:
        root = docs_dir / collection.source_dir
        author_data = _load_yaml(root / ".authors.yml").get("authors", {})
        if not isinstance(author_data, dict):
            raise ValueError(f"Expected authors mapping in {root / '.authors.yml'}")
        authors = {
            str(key): str(value.get("name", key))
            for key, value in author_data.items()
            if isinstance(value, dict)
        }
        posts = tuple(
            sorted(
                (
                    _load_post(docs_dir, collection, path)
                    for path in (root / "posts").glob("*.md")
                ),
                key=lambda post: (post.published, post.title),
                reverse=True,
            )
        )
        if not posts:
            raise ValueError(f"No Markdown posts found in {root / 'posts'}")
        loaded.append((collection, posts, authors))
    return loaded


def _load_post(docs_dir: Path, collection: Collection, path: Path) -> Post:
    metadata, body = _body(path.read_text(encoding="utf-8"))
    title = str(metadata.get("title", "")).strip()
    published = metadata.get("date")
    if not title:
        raise ValueError(f"Post title is missing: {path}")
    if not isinstance(published, date):
        raise ValueError(f"Post date is missing or invalid: {path}")

    authors_value = metadata.get("authors", [])
    if not isinstance(authors_value, list):
        raise ValueError(f"Post authors must be a list: {path}")
    authors = tuple(str(value) for value in authors_value)

    taxonomy_values: tuple[str, ...] = ()
    if collection.taxonomy:
        raw_values = metadata.get(collection.taxonomy, [])
        if not isinstance(raw_values, list):
            raise ValueError(
                f"Post {collection.taxonomy} must be a list: {path}"
            )
        taxonomy_values = tuple(str(value) for value in raw_values)

    slug = _route_slug(title)
    if collection.dated_routes:
        route = (
            collection.route_dir
            / f"{published.year:04d}"
            / f"{published.month:02d}"
            / f"{published.day:02d}"
            / f"{slug}.md"
        )
    else:
        route = collection.route_dir / f"{slug}.md"

    source = PurePosixPath(path.relative_to(docs_dir).as_posix())
    return Post(
        source=source,
        title=title,
        published=published,
        authors=authors,
        taxonomy_values=taxonomy_values,
        metadata=metadata,
        body=_rewrite_links(
            body.replace("<!-- more -->", "").strip(), source, docs_dir
        ),
        route=route,
        heading_anchor=_heading_slug(_NUMBER_SUFFIX_RE.sub("", title)),
    )


def _body(markdown: str) -> tuple[dict[str, object], str]:
    lines = markdown.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, markdown
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() in {"---", "..."}:
            metadata = yaml.safe_load("".join(lines[1:index])) or {}
            if not isinstance(metadata, dict):
                raise ValueError("Markdown front matter must be a mapping")
            return metadata, "".join(lines[index + 1 :])
    raise ValueError("Markdown front matter is not closed")


def _load_yaml(path: Path) -> dict[str, object]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return value


def _render_post(post: Post, authors: dict[str, str]) -> str:
    metadata = dict(post.metadata)
    front_matter = yaml.safe_dump(
        metadata,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).strip()
    return (
        f"---\n{front_matter}\n---\n\n"
        f"# {post.title} {{#{post.heading_anchor}}}\n\n"
        f"{_metadata_line(post, authors)}\n\n"
        f"{post.body}\n"
    )


def _render_listing(
    preamble: str, posts: tuple[Post, ...], authors: dict[str, str]
) -> str:
    sections = [preamble.strip()]
    for post in posts:
        url = f"/{post.route.with_suffix('.html').as_posix()}"
        sections.append(
            f"## [{post.title}]({url}) {{#{post.heading_anchor}}}\n\n"
            f"{_metadata_line(post, authors)}\n\n"
            f"{post.body}"
        )
    return "\n\n---\n\n".join(section for section in sections if section).rstrip() + "\n"


def _metadata_line(post: Post, authors: dict[str, str]) -> str:
    names = ", ".join(authors.get(author, author) for author in post.authors)
    words = len(_WORD_RE.findall(post.body))
    minutes = max(1, math.ceil(words / 200))
    formatted = (
        f"{_MONTHS[post.published.month - 1]} {post.published.day}, "
        f"{post.published.year}"
    )
    parts = [formatted]
    if names:
        parts.append(names)
    parts.append(f"{minutes} min read")
    return f"*{' · '.join(parts)}*"


def _browse_links(collection: Collection, posts: tuple[Post, ...]) -> str:
    years = sorted({post.published.year for post in posts}, reverse=True)
    archive = " · ".join(
        f"[{year}]"
        f"(/{collection.route_dir.as_posix()}/archive/{year}.html)"
        for year in years
    )
    lines = [f"**Archive:** {archive}"]
    if collection.taxonomy:
        values = sorted(
            {value for post in posts for value in post.taxonomy_values},
            key=str.casefold,
        )
        categories = " · ".join(
            f"[{value}]"
            f"(/{collection.route_dir.as_posix()}/category/"
            f"{_heading_slug(value)}.html)"
            for value in values
        )
        if categories:
            lines.append(f"**Categories:** {categories}")
    return "\n\n".join(lines)


def _redirect_html(site_url: str, target: PurePosixPath) -> str:
    relative = f"/{target.as_posix()}"
    canonical = f"{site_url.rstrip('/')}{relative}"
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="robots" content="noindex">
    <meta http-equiv="refresh" content="0; url={escape(relative, quote=True)}">
    <link rel="canonical" href="{escape(canonical, quote=True)}">
    <title>Blog post moved</title>
  </head>
  <body>
    {_REDIRECT_MARKER}
    <p>This blog post moved to <a href="{escape(relative, quote=True)}">its canonical URL</a>.</p>
  </body>
</html>"""


def _rewrite_links(
    markdown: str, source: PurePosixPath, docs_dir: Path
) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith(("/", "#")):
            return match.group(0)

        resolved = PurePosixPath(
            posixpath.normpath(
                posixpath.join(source.parent.as_posix(), parsed.path)
            )
        )
        if resolved == PurePosixPath("..") or resolved.as_posix().startswith("../"):
            raise ValueError(f"Post link escapes docs directory: {source} -> {target}")

        if resolved.parent in {
            PurePosixPath("blogs/posts"),
            PurePosixPath("personal/posts"),
        } and resolved.suffix == ".md":
            target_post = _post_route_for_source(resolved, docs_dir)
            path = f"/{target_post.with_suffix('.html').as_posix()}"
        elif resolved.suffix == ".md":
            path = f"/{resolved.with_suffix('.html').as_posix()}"
        else:
            path = f"/{resolved.as_posix()}"

        rewritten = urlunsplit(("", "", path, parsed.query, parsed.fragment))
        angle = "<" if match.group("angle") else ""
        close = ">" if match.group("close") else ""
        return f"{match.group('prefix')}{angle}{rewritten}{close}"

    return _LINK_TARGET_RE.sub(replace, markdown)


def _post_route_for_source(
    source: PurePosixPath, docs_dir: Path
) -> PurePosixPath:
    for collection in _COLLECTIONS:
        if source.parent != collection.source_dir / "posts":
            continue
        root = docs_dir / source
        if not root.is_file():
            raise ValueError(f"Linked post source does not exist: {source}")
        metadata, _ = _body(root.read_text(encoding="utf-8"))
        title = str(metadata.get("title", "")).strip()
        published = metadata.get("date")
        if not title or not isinstance(published, date):
            raise ValueError(f"Linked post metadata is invalid: {source}")
        slug = _route_slug(title)
        if collection.dated_routes:
            return (
                collection.route_dir
                / f"{published.year:04d}"
                / f"{published.month:02d}"
                / f"{published.day:02d}"
                / f"{slug}.md"
            )
        return collection.route_dir / f"{slug}.md"
    raise ValueError(f"Unsupported linked post source: {source}")


def _route_slug(value: str) -> str:
    value = _NUMBER_SUFFIX_RE.sub("", value).strip().lower()
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    return re.sub(r"\s", "-", value).strip("-")


def _heading_slug(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
