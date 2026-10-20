# AI documentation research and maintenance

Research checked on 20 October 2026.

## Finding and recommendation

Magewire already has the requested build-time system in
[`scripts/generate_ai_docs.py`](scripts/generate_ai_docs.py) and
[the Documentation workflow](.github/workflows/ci.yml). Keep this shared
implementation and regenerate its outputs during every documentation build.

At the time of this review, the public `llms.txt` and `llms-full.txt` endpoints
both returned HTTP 200 with `Content-Type: text/plain; charset=utf-8`. The index
linked to 98 Markdown pages; the full file contained 98 source documents.
The index was 18,727 bytes and the full file was 488,763 bytes. These are
observations of the deployed version, not size limits. The repository's Pages
API reported `build_type: workflow` and `status: built`.

## What the files should contain

The [llms.txt proposal](https://llmstxt.org/) uses Markdown: an H1 project name,
an optional summary blockquote and explanatory text, then H2 sections of
annotated links. The proposal recommends linking to clean per-page Markdown
and keeping the index small so an agent can retrieve the detail it needs. It
also recommends `rel="describedby"` and Markdown alternate links for discovery.
This is a proposal, and publishing a file does not ensure every assistant
will discover or use it.

`llms-full.txt` is an ecosystem convention with no prescribed format in that
proposal. [Mintlify's implementation](https://www.mintlify.com/docs/ai/llmstxt)
combines page titles, source URLs, descriptions, and full Markdown. It also
derives index order from navigation and offers per-page `.md` links. These
are useful precedents for Magewire's existing source-derived exports.

| Output | Magewire behavior |
| --- | --- |
| `/llms.txt` | Project summary, Magewire version, usage guidance, topic links, and every navigated page's absolute Markdown URL and short summary. |
| `/llms-full.txt` | Complete navigated Markdown in navigation order, with source boundaries and canonical HTML URLs; repeated pages are included once. |
| `/ai/<section>.txt` | Complete context for one top-level navigation section. |
| `/index.md` and `/pages/**/*.md` | Individual Markdown pages alongside their HTML counterparts. |

Use the index and individual pages as the normal entry point. The full file
is useful for tools with enough context capacity; the section bundles provide
a smaller alternative. There is no need to invent a fixed word limit or
truncate the full documentation silently.

## Source and corpus rules

The canonical inputs are `mkdocs.yml`, navigated Markdown under `docs/`, and
referenced files under `includes/`. The generator expands the supported
`include()` macro, removes presentation-only Jinja raw controls and YAML
front matter, and preserves documentation and code examples. The summary,
documentation version, and includes directory are configured under `extra`
in `mkdocs.yml`.

Navigation defines inclusion and ordering. Add a new guide to `nav` to include
it automatically. Blog posts, Personal pages, and unlisted drafts remain
outside this corpus. The generator does not independently apply `noindex` or
visibility metadata; keeping a page out of this export is not access control.
Each aggregate identifies Magewire 3.x and cautions against assuming that
Laravel Livewire APIs apply to Magewire.

Generation is deterministic and requires no model calls, credentials, paid
service, or live-site crawl. The generated files are ignored build artifacts
under `site/`, so maintaining duplicate content or committing refreshed
exports is unnecessary.

## How every merge updates the files

GitHub's [`push` event](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#push)
runs for commits pushed to a matching branch. A PR merged into `main` updates
that branch, which triggers the existing workflow with the merged sources.

1. PRs targeting `main` run the focused regression checks, strict clean site
   build, AI generation, site validation, and production URL compatibility
   check. They do not deploy.
2. A push to `main`, including a merged PR, repeats the same checks against
   the resulting commit.
3. After the HTML build and blog finalization, the workflow runs
   `python scripts/generate_ai_docs.py --config-file mkdocs.yml --output-dir site`.
4. `scripts/validate_site.py` verifies required resources and compares every
   AI resource byte-for-byte with a fresh, in-memory rendering of the current
   sources. It reports stale files without rewriting them. Existing checks
   also catch unexpected Markdown files and topic bundles.
5. Only a successful `main` push uploads and deploys `site/` as one Pages
   artifact, including HTML, raw Markdown, the index, full text, and topics.

This follows GitHub's documented
[custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
pattern: upload the build artifact, then deploy it in a dependent job.
The clean build removes exports for deleted pages and sections. If generation
or validation fails, deployment cannot publish that build and the previous
site remains available. New content becomes public after a successful
deployment, not at the instant the merge completes.

The current workflow has no path filter, so changes to includes, navigation,
configuration, or the generator also trigger rebuilding. Keep AI generation
in this pipeline; an independent merge-only workflow, scheduled crawler, or
commit-back bot would introduce another update path. For merge queues, add
the `merge_group` trigger before requiring this workflow in the queue, as
described in GitHub's workflow-event documentation.

## Maintenance and verification

Edit canonical Markdown and includes. Add, rename, or remove navigation entries
with the corresponding page change. Run the [README build sequence](README.md)
to preview the same artifact as CI; `zensical serve` alone does not execute
the external post-build generator. The retained Material rollback invokes
the same generator through the `hooks` entry instead.

The regression checks exercise deterministic generation, stale outputs,
edited source pages and includes, new navigated pages, and removal after a
clean build:

```sh
python -m unittest discover -s tests -p 'test_*.py'
```

After deployment, check the Documentation workflow and fetch `/llms.txt`,
`/llms-full.txt`, a changed page's `.md` URL, and its section bundle. Confirm
HTTP 200, a plain-text response rather than HTML, and the expected changed
content. Merely checking the status code can miss a preview server's HTML
fallback. The published index should link to each current Markdown page.

HTML discovery metadata can be added when Zensical offers a suitable native
mechanism. This implementation exposes the files at conventional root URLs
and links them from the documentation usage guide without depending on a
theme template override.
