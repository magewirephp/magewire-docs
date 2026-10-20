# Magewire PHP - Documentation

## AI documentation and automatic updates

The site publishes [`llms.txt`](https://docs.magewirephp.nl/llms.txt), a compact
index linking to Markdown pages, and
[`llms-full.txt`](https://docs.magewirephp.nl/llms-full.txt), the complete
navigated documentation. Smaller section bundles live under `/ai/`.

Every PR targeting `main` builds and validates these resources. When the PR is
merged, the resulting push to `main` regenerates them from the merged Markdown
and `mkdocs.yml` navigation, then deploys them with the HTML in the same GitHub
Pages artifact. CI rejects missing resources and content that differs from the
current sources. Generated files live in ignored `site/`; edit the source docs
and includes, and add new pages to `nav` in `mkdocs.yml`.

See [AI documentation research and maintenance](ai-documentation.md) for the
format choices, corpus rules, deployment flow, and verification procedure.

## Local Zensical build

The production documentation runs on Zensical, uses privacy-friendly system fonts, and rejects third-party runtime assets during validation. A build-time compatibility adapter derives the Blog pages from their canonical Markdown before Zensical builds the site.

Use Python 3.14 to match CI. After installing dependencies, the focused AI
documentation checks can also run independently with
`python -m unittest discover -s tests -p 'test_*.py'`.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_blog.py prepare --docs-dir docs --output-dir .build/docs
zensical build --config-file .build-mkdocs.yml --clean --strict
python scripts/build_blog.py finalize --docs-dir docs --site-dir site
python scripts/generate_ai_docs.py --config-file mkdocs.yml --output-dir site
python scripts/validate_site.py --config-file mkdocs.yml --site-dir site
python scripts/compare_production_urls.py --manifest tests/production-url-manifest.json --site-dir site
python3 -m http.server 8000 --directory site
```

Visit `http://localhost:8000/`. This serves the same static artifact CI uploads, including the source-derived Blog pages, `/llms.txt`, `/llms-full.txt`, `/ai/*.txt`, and per-page Markdown such as `/pages/concepts/fragments.md`. The temporary `.build/docs` tree and `.build-mkdocs.yml` configuration are generated from the canonical post Markdown and can be deleted at any time. See [`docs-migration.md`](docs-migration.md) for the migration findings and compatibility record.

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
