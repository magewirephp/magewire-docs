"""Compare a built site with the captured production URL and anchor contract."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import xml.etree.ElementTree as ElementTree


_SITEMAP_NAMESPACE = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class HeadingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag not in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            return
        values = {name: value for name, value in attrs if value is not None}
        if values.get("id"):
            self.anchors.add(values["id"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare generated URLs and heading anchors with production"
    )
    parser.add_argument(
        "--manifest", default="tests/production-url-manifest.json", type=Path
    )
    parser.add_argument("--site-dir", default="site", type=Path)
    args = parser.parse_args()

    site_dir = args.site_dir.resolve()
    manifest = _load_manifest(args.manifest)
    production = {
        PurePosixPath(path): set(anchors)
        for path, anchors in manifest["pages"].items()
    }
    deferred_missing = {
        PurePosixPath(path): reason
        for path, reason in manifest["deferred_missing"].items()
    }
    deferred_anchor_loss = {
        PurePosixPath(path): reason
        for path, reason in manifest["deferred_anchor_loss"].items()
    }
    deferred_sitemap_missing = {
        PurePosixPath(path): reason
        for path, reason in manifest["deferred_sitemap_missing"].items()
    }
    candidate = {
        PurePosixPath(path.relative_to(site_dir).as_posix())
        for path in site_dir.rglob("*.html")
        if path.name != "404.html"
    }
    errors: list[str] = []

    for label, exceptions in (
        ("deferred-missing", deferred_missing),
        ("deferred-anchor-loss", deferred_anchor_loss),
        ("deferred-sitemap-missing", deferred_sitemap_missing),
    ):
        for path in sorted(exceptions.keys() - production.keys()):
            errors.append(f"{label} URL is not in the production manifest: /{path}")

    missing = production.keys() - candidate
    unexpected_missing = missing - deferred_missing.keys()
    known_missing = missing & deferred_missing.keys()
    stale_deferred = deferred_missing.keys() - missing

    for path in sorted(unexpected_missing):
        errors.append(f"production URL is missing from candidate: /{path}")
    for path in sorted(stale_deferred):
        errors.append(
            f"resolved production URL still has a deferred-missing entry: /{path}"
        )

    lost_anchors: dict[PurePosixPath, set[str]] = {}
    for path in sorted(production.keys() & candidate):
        current = _heading_anchors(site_dir / path)
        missing_anchors = production[path] - current
        if missing_anchors:
            lost_anchors[path] = missing_anchors
            if path not in deferred_anchor_loss:
                for anchor in sorted(missing_anchors):
                    errors.append(
                        f"production heading anchor is missing: /{path}#{anchor}"
                    )
    for path in sorted(deferred_anchor_loss.keys() - lost_anchors.keys()):
        errors.append(
            f"resolved production anchors still have a deferred-loss entry: /{path}"
        )

    sitemap_urls = _load_candidate_sitemap(site_dir / "sitemap.xml", manifest, errors)
    known_sitemap_missing: set[PurePosixPath] = set()
    if sitemap_urls is not None:
        preserved = production.keys() & candidate
        sitemap_missing = preserved - sitemap_urls
        known_sitemap_missing = sitemap_missing & deferred_sitemap_missing.keys()
        for path in sorted(sitemap_missing - deferred_sitemap_missing.keys()):
            errors.append(f"preserved production URL is absent from sitemap.xml: /{path}")
        for path in sorted(deferred_sitemap_missing.keys() - sitemap_missing):
            errors.append(
                f"resolved sitemap URL still has a deferred-missing entry: /{path}"
            )
        for path in sorted(sitemap_urls - candidate):
            errors.append(f"sitemap.xml points to missing candidate HTML: /{path}")

    if errors:
        print(f"Production URL comparison failed with {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    added = candidate - production.keys()
    preserved = production.keys() & candidate
    production_anchor_count = sum(len(anchors) for anchors in production.values())
    known_lost_anchor_count = sum(
        len(anchors)
        for path, anchors in lost_anchors.items()
        if path in deferred_anchor_loss
    )
    print(
        f"Compared {len(production)} production URLs and {production_anchor_count} "
        f"heading anchors: {len(preserved)} URLs preserved, "
        f"{len(known_missing)} deferred URL differences, "
        f"{len(added)} candidate-only URLs, "
        f"{known_lost_anchor_count} deferred lost anchors, "
        f"{len(known_sitemap_missing)} deferred sitemap omissions"
    )
    for path in sorted(known_missing):
        print(f"DEFERRED URL /{path}: {deferred_missing[path]}")
    for path in sorted(lost_anchors.keys() & deferred_anchor_loss.keys()):
        print(
            f"DEFERRED ANCHORS /{path} ({len(lost_anchors[path])} anchors): "
            f"{deferred_anchor_loss[path]}"
        )
    for path in sorted(known_sitemap_missing):
        print(
            f"DEFERRED SITEMAP /{path}: {deferred_sitemap_missing[path]}"
        )


def _load_manifest(path: Path) -> dict[str, object]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeError) as exception:
        raise SystemExit(f"Cannot read production URL manifest {path}: {exception}")
    if not isinstance(manifest, dict):
        raise SystemExit("Production URL manifest must be a JSON object")
    if not isinstance(manifest.get("pages"), dict):
        raise SystemExit("Production URL manifest must contain a pages object")
    if not isinstance(manifest.get("deferred_missing"), dict):
        raise SystemExit("Production URL manifest must contain a deferred_missing object")
    if not isinstance(manifest.get("deferred_anchor_loss"), dict):
        raise SystemExit(
            "Production URL manifest must contain a deferred_anchor_loss object"
        )
    if not isinstance(manifest.get("deferred_sitemap_missing"), dict):
        raise SystemExit(
            "Production URL manifest must contain a deferred_sitemap_missing object"
        )
    return manifest


def _heading_anchors(path: Path) -> set[str]:
    parser = HeadingParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.anchors


def _load_candidate_sitemap(
    path: Path, manifest: dict[str, object], errors: list[str]
) -> set[PurePosixPath] | None:
    if not path.is_file():
        errors.append("candidate sitemap.xml is missing")
        return None
    try:
        root = ElementTree.fromstring(path.read_text(encoding="utf-8"))
    except (ElementTree.ParseError, OSError, UnicodeError) as exception:
        errors.append(f"candidate sitemap.xml is invalid: {exception}")
        return None

    site_url = str(manifest.get("site_url", "")).rstrip("/")
    if not site_url:
        errors.append("production URL manifest has no site_url")
        return None
    prefix = f"{site_url}/"
    urls: set[PurePosixPath] = set()
    for location in root.findall(
        f"{_SITEMAP_NAMESPACE}url/{_SITEMAP_NAMESPACE}loc"
    ):
        if not location.text or not location.text.startswith(prefix):
            errors.append(f"candidate sitemap URL has the wrong origin: {location.text}")
            continue
        urls.add(PurePosixPath(location.text.removeprefix(prefix)))
    return urls


if __name__ == "__main__":
    main()
