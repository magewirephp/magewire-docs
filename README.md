# Magewire PHP - Documentation

## Zensical compatibility preview

The migration runs from the existing `mkdocs.yml`, uses privacy-friendly system fonts, and rejects third-party runtime assets during validation. This branch contains the candidate Zensical Pages workflow, but it cannot deploy until merged to `main` and the repository's Pages source is switched to GitHub Actions during cutover.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
zensical build --config-file mkdocs.yml --clean --strict
python scripts/generate_ai_docs.py --config-file mkdocs.yml --output-dir site
python scripts/validate_site.py --config-file mkdocs.yml --site-dir site
python scripts/compare_production_urls.py --manifest tests/production-url-manifest.json --site-dir site
python3 -m http.server 8000 --directory site
```

Visit `http://localhost:8000/`. This serves the same static artifact CI uploads, including `/llms.txt`, `/llms-full.txt`, `/ai/*.txt`, and per-page Markdown such as `/pages/concepts/fragments.md`. For a live-reloading HTML-only preview, use `zensical serve`; Zensical's preview rebuild does not run the separate AI generator. See [`docs-migration.md`](docs-migration.md) for the completed Phase 0–14 findings and cutover-readiness record.

## Material rollback preview

The Material container is retained temporarily for rollback and compatibility comparisons. It is not the candidate production deployment path.

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
