# Magewire PHP - Documentation

## Local Zensical build

The production documentation runs on Zensical, uses privacy-friendly system fonts, and rejects third-party runtime assets during validation. A build-time compatibility adapter derives the Blog pages from their canonical Markdown before Zensical builds the site.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_blog.py prepare --docs-dir docs --output-dir .build/docs
zensical build --config-file mkdocs.zensical.yml --clean --strict
python scripts/build_blog.py finalize --docs-dir docs --site-dir site
python scripts/generate_ai_docs.py --config-file mkdocs.yml --output-dir site
python scripts/validate_site.py --config-file mkdocs.yml --site-dir site
python scripts/compare_production_urls.py --manifest tests/production-url-manifest.json --site-dir site
python3 -m http.server 8000 --directory site
```

Visit `http://localhost:8000/`. This serves the same static artifact CI uploads, including the source-derived Blog pages, `/llms.txt`, `/llms-full.txt`, `/ai/*.txt`, and per-page Markdown such as `/pages/concepts/fragments.md`. The temporary `.build/docs` tree is generated from the canonical post Markdown and can be deleted at any time. See [`docs-migration.md`](docs-migration.md) for the migration findings and compatibility record.

## Material rollback preview

The Material container is retained temporarily for rollback and compatibility comparisons. It is not the production deployment path.

To contribute to the documentation, follow these steps:

1. Build the pinned rollback image:
   ```shell
   docker build -t magewirephp/mkdocs-material .
   ```

2. Run locally:
   ```shell
   docker run --rm -it -p 8000:8000 -v ${PWD}:/docs magewirephp/mkdocs-material
   ```

3. Visit:
   ```shell
   http://0.0.0.0:8000/magewire-docs/
   ```
