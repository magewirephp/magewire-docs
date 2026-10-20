# Magewire PHP - Documentation

## AI documentation snapshots

The two committed files, [`docs/llms.txt`](docs/llms.txt) and
[`docs/llms-full.txt`](docs/llms-full.txt), are served as plain text at
[`/llms.txt`](https://docs.magewirephp.nl/llms.txt) and
[`/llms-full.txt`](https://docs.magewirephp.nl/llms-full.txt). Zensical copies
them into the site as static assets. The index links to the published HTML
guides; the full file contains the navigated documentation in one place.

Refresh them with an agent when needed, for example once a month. Normal docs
builds publish the committed snapshots without regenerating them. CI checks
that the routes contain the committed text and that their local links resolve;
it allows the snapshots to lag behind documentation edits between refreshes.

Use this prompt for the next refresh:

```text
Refresh docs/llms.txt and docs/llms-full.txt from the current Magewire docs.
Follow the canonical mkdocs.yml navigation, excluding unlisted pages and blogs.
Keep llms.txt a compact Markdown index with absolute links to published .html
routes and a link to llms-full.txt. Put the complete navigated content in
llms-full.txt, expanding includes, preserving code examples, and resolving
relative links against each original page's published URL. Include the
Magewire version, today's refresh date, and a warning that Livewire APIs may
differ. Create only these two AI exports. Run the README build and validation
commands, check both text routes through a local HTTP server, and make a PR.
```

## Local Zensical build

The production documentation runs on Zensical, uses privacy-friendly system fonts, and rejects third-party runtime assets during validation. A build-time compatibility adapter derives the Blog pages from their canonical Markdown before Zensical builds the site.

Use Python 3.14 to match CI.

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_blog.py prepare --docs-dir docs --output-dir .build/docs
zensical build --config-file .build-mkdocs.yml --clean --strict
python scripts/build_blog.py finalize --docs-dir docs --site-dir site
python scripts/validate_site.py --config-file mkdocs.yml --site-dir site
python scripts/compare_production_urls.py --manifest tests/production-url-manifest.json --site-dir site
python3 -m http.server 8000 --directory site
```

Visit `http://localhost:8000/`, `http://localhost:8000/llms.txt`, or
`http://localhost:8000/llms-full.txt`. This serves the same static artifact CI
uploads, including the source-derived Blog pages and both committed AI
snapshots. The temporary `.build/docs` tree and `.build-mkdocs.yml`
configuration are generated from the canonical post Markdown and can be
deleted at any time. See [`docs-migration.md`](docs-migration.md) for the
migration findings and compatibility record.

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
