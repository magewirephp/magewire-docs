"""Exercise source changes and stale artifacts without a network or site build."""

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_ai_docs import _generate, _load_sources, _render_outputs
from validate_site import _check_ai_freshness


class AIDocumentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.includes = self.root / "includes"
        self.includes.mkdir()
        self.site = self.root / "site"
        self.site.mkdir()
        self.config_file = self.root / "mkdocs.yml"
        self.sources = ["index.md", "guide.md"]
        self.config = {
            "site_name": "Example Docs",
            "site_url": "https://docs.example.com",
            "use_directory_urls": False,
            "extra": {
                "ai_docs": {
                    "summary": "Documentation for the example project.",
                    "documentation_version": "Example 3.x",
                }
            },
            "nav": [{"Guides": self.sources}],
        }
        self.write_config()
        (self.docs / "index.md").write_text("# Home\n\nStart here.\n", encoding="utf-8")
        (self.docs / "guide.md").write_text(
            '# Guide\n\nGuide before change.\n\n{{ include("example.md") }}\n',
            encoding="utf-8",
        )
        (self.includes / "example.md").write_text(
            "```php\necho 'Included example';\n```\n", encoding="utf-8"
        )
        (self.docs / "unlisted.md").write_text(
            "# Unlisted draft\n\nNot published in AI context.\n", encoding="utf-8"
        )
        self.build()

    def write_config(self) -> None:
        self.config_file.write_text(yaml.safe_dump(self.config), encoding="utf-8")

    def load(self):
        return _load_sources(self.config_file, self.site)

    def build(self) -> None:
        # Only the generator's canonical-target check needs HTML fixtures.
        for source in self.sources:
            (self.site / Path(source).with_suffix(".html")).write_text(
                "<h1>Example page</h1>", encoding="utf-8"
            )
        _generate(*self.load())

    def freshness_errors(self) -> list[str]:
        errors: list[str] = []
        _check_ai_freshness(self.site, _render_outputs(*self.load()), errors)
        return errors

    def test_clean_build_matches_sources_and_is_deterministic(self) -> None:
        before = {path: path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(self.freshness_errors(), [])
        self.build()
        after = {path: path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        self.assertFalse((self.site / "unlisted.md").exists())
        self.assertNotIn("Unlisted draft", (self.site / "llms-full.txt").read_text())

    def test_stale_content_is_rejected_without_repairing_it(self) -> None:
        for relative in ("llms.txt", "llms-full.txt", "ai/guides.txt", "guide.md"):
            with self.subTest(resource=relative):
                path = self.site / relative
                original = path.read_text(encoding="utf-8")
                stale = original.replace("Guide before change.", "Guide from an old PR.")
                self.assertNotEqual(original, stale)
                path.write_text(stale, encoding="utf-8")
                self.assertEqual(len(errors := self.freshness_errors()), 1)
                self.assertIn(f"AI documentation is stale: {relative};", errors[0])
                self.assertEqual(path.read_text(encoding="utf-8"), stale)
                path.write_text(original, encoding="utf-8")

    def test_source_edit_requires_regeneration(self) -> None:
        path = self.docs / "guide.md"
        path.write_text(
            path.read_text().replace("Guide before change.", "Guide after merged PR."),
            encoding="utf-8",
        )
        self.assertEqual(len(errors := self.freshness_errors()), 4)
        for relative in ("llms.txt", "llms-full.txt", "ai/guides.txt", "guide.md"):
            self.assertTrue(any(f"stale: {relative};" in error for error in errors))
        self.build()
        self.assertEqual(self.freshness_errors(), [])
        self.assertIn("Guide after merged PR.", (self.site / "llms-full.txt").read_text())

    def test_include_edit_updates_full_topic_and_raw_content(self) -> None:
        (self.includes / "example.md").write_text(
            "```php\necho 'Updated included example';\n```\n", encoding="utf-8"
        )
        self.assertEqual(len(self.freshness_errors()), 3)
        self.build()
        self.assertEqual(self.freshness_errors(), [])
        for relative in ("llms-full.txt", "ai/guides.txt", "guide.md"):
            self.assertIn("Updated included example", (self.site / relative).read_text())

    def test_new_navigated_page_is_included_on_next_build(self) -> None:
        (self.docs / "new.md").write_text("# New page\n\nNew PR content.\n", encoding="utf-8")
        self.sources.append("new.md")
        self.write_config()
        self.build()
        self.assertEqual(self.freshness_errors(), [])
        self.assertIn("https://docs.example.com/new.md", (self.site / "llms.txt").read_text())
        self.assertIn("New PR content.", (self.site / "llms-full.txt").read_text())
        self.assertIn("New PR content.", (self.site / "ai/guides.txt").read_text())
        self.assertTrue((self.site / "new.md").is_file())

    def test_removed_page_is_absent_after_clean_build(self) -> None:
        self.sources.remove("guide.md")
        (self.docs / "guide.md").unlink()
        self.write_config()
        # CI uses a clean site build, which removes obsolete resources first.
        shutil.rmtree(self.site)
        self.site.mkdir()
        self.build()
        self.assertEqual(self.freshness_errors(), [])
        self.assertNotIn("guide.md", (self.site / "llms.txt").read_text())
        self.assertNotIn("SOURCE DOCUMENT: docs/guide.md", (self.site / "llms-full.txt").read_text())
        self.assertFalse((self.site / "guide.md").exists())


if __name__ == "__main__":
    unittest.main()
