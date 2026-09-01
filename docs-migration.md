# Zensical migration notes

Status: Phase 0 through Phase 14 complete; final-cutover readiness proven without changing production, 2026-09-01

Branch: `migration/zensical`
Tested versions: Material for MkDocs 9.7.7, MkDocs 1.6.1, Zensical 0.0.57, mkdocs-macros-plugin 1.5.0, Python 3.14.4

This work intentionally leaves `mkdocs.yml`, the Markdown sources, and a pinned Material rollback image in place. The compatibility audit is complete, the modern theme is selected, native configuration was evaluated and deliberately deferred, a Zensical GitHub Pages workflow is prepared but not active in production, the source-derived AI documentation layer including raw page-level Markdown is implemented, and its complete static artifact and production URL contract are validated in CI. Privacy/offline behavior is resolved with system fonts and an automated third-party asset gate. The safe cleanup audit and cutover-readiness proof are complete; the production Pages setting and `main` branch have not been changed.

## Current project inventory

### Configuration and navigation

- `mkdocs.yml` defines the canonical site URL and sets `use_directory_urls: false`. Ordinary pages therefore publish as `.html` paths; preserving this setting preserves those paths.
- The explicit navigation has eight visible top-level sections: Getting Started, Essentials, Features, Directives, Concepts, Theming, Admin, and Advanced. Advanced contains the Javascript and Architecture subsections. The Blog, Personal blog, and Magewire Flakes page are intentionally absent from navigation; their sources are still built.
- Enabled theme features cover pruned navigation, breadcrumbs/path display, previous/next footer links, instant navigation and progress, tracking, top navigation, section indexes, and code copy/annotation/select controls. Tabbed navigation and the auto-hiding header were removed after the Phase 1 proof.
- The theme explicitly selects the `modern` variant, disables hosted web fonts in favor of the browser's system font stack, uses Zensical's native system/light/dark palette controls, and disables the generator label. No footer social links are configured.
- There is no versioning, redirect plugin, social-card plugin, or extra JavaScript configuration.

### Extensions, plugins, hooks, and environment

- Python Markdown/PyMdown extensions: abbreviations, attribute lists, highlighting (including custom `php-inline`), inline highlighting, snippets, superfences, admonitions, collapsible details, caret, mark, tilde, and Material emoji/icon rendering.
- Plugins: two Material blog instances (`blogs` and `personal`), tags, search with a custom separator, and macros with `includes/` as its include directory.
- `main.py` defines the custom `include()` macro used by 58 Markdown pages. It expands shared Markdown fragments and accepts placeholder arguments.
- `scripts/generate_ai_docs.py` is both the Material hook and the Zensical post-build generator. It writes `site/llms.txt`, `site/llms-full.txt`, and the navigation-derived topic bundles.
- No environment variables are required by the active configuration. The former Material privacy plugin setting was removed after system fonts made remote font localization unnecessary and the plugin's implicit Mermaid download made strict offline rollback builds fail.

### Customization

- The legacy `docs/stylesheets/style.css` override was removed after the Phase 1 proof so the preview uses Zensical's default theme styling. It previously customized Material-era header, tab, button, table, and admonition selectors.
- The empty custom analytics integration and its template override were removed after the Phase 1 proof. No template overrides remain.
- There is no configured custom JavaScript. Image assets include Magewire logos, a GIF, and one avatar. Icons come from the theme's bundled icon sets.

### Markdown usage found

- 107 Markdown sources in `docs/`, including 98 under `docs/pages/` and six blog/personal posts. Phase 13 synchronized the Hyvä CSP Script Bootstrap page added to `main` after this branch was created.
- Admonitions on 31 source/include files (41 declarations), including one collapsible detail block.
- Fenced code on 83 source/include files, primarily PHP, XML, HTML, shell, and JavaScript, plus inline code and highlighted code.
- Tables on 40 files, attribute lists on three files, raw/custom HTML examples on at least 44 files, and Markdown cross-page links on 70 files.
- Shared macro includes are used extensively. No authored content tabs, code annotations, direct snippet directives, footnotes, or explicit custom heading IDs were found.

### GitHub Pages delivery at the start of the migration

- `.github/workflows/ci.yml` runs only for pushes to `main`; pull requests do not build or deploy.
- It installs unpinned `mkdocs-material` and `mkdocs-macros-plugin`, then runs `mkdocs gh-deploy --force` with `contents: write`.
- Deployment is the MkDocs `gh-deploy`/`gh-pages` branch model, not a GitHub Pages artifact workflow.
- `docs/CNAME` contains `docs.magewirephp.nl` and is copied to the generated site. No migration-branch deployment was added.

## Phase 1 build proof

The unchanged project builds successfully with both baselines:

```text
mkdocs build --strict
zensical build
zensical build --strict
zensical serve --dev-addr 127.0.0.1:8123
```

The Material strict build completed without project warnings. The exact `zensical build` command completed with `No issues found`, and the preview server served representative Getting Started, Concepts, Security, and search resources.

### Compatibility results

| Area | Result in Zensical 0.0.57 | Evidence / required action |
| --- | --- | --- |
| Existing `mkdocs.yml` | Works directly | No native `zensical.toml` was introduced. Official guidance currently recommends retaining YAML for existing projects. |
| Ordinary page paths | Compatible | All 97 `docs/pages/` outputs plus the root index use the same relative HTML paths as the Material baseline. |
| Authored anchors | Compatible | All 570 authored heading IDs across the root index and `pages/` matched. One page without an authored H1 gains a Zensical-only internal `#__skip` ID; no prior authored anchor is replaced. |
| Navigation and theme features | Build and render | The configured hierarchy, breadcrumbs, tables of contents, previous/next controls, system/light/dark palettes, and code controls are present in generated HTML. Automated browser inspection was unavailable; responsive and interactive behavior remains a manual-preview check. |
| Markdown and PyMdown | Works for used samples | Includes, headings, fenced/highlighted code, inline code, admonitions/details, tables, attribute lists, icons, raw HTML, and cross-page links render without content edits. |
| Macros | Works directly | Zensical expands the custom `include()` macro, including arguments, even though the separately installed plugin is not needed by the Zensical runtime. Keep the plugin for the Material rollback path. |
| Search | Works | `search.json` contains 623 title/heading/body entries and retains the configured separator. The root page, headings, Security entries, and body phrases are indexed. |
| Custom theme overrides | Intentionally removed | The legacy stylesheet and empty analytics template override were removed after this proof so the preview follows Zensical defaults. |
| `CNAME` and static assets | Works | `CNAME`, images, theme assets, sitemap, and search output are generated. |
| MkDocs hook | **Unsupported natively / adapted** | Zensical still skips the `hooks` setting, but Phases 6–10 moved the AI logic into a dual-purpose generator. CI invokes it after Zensical; Material can load the same file as a hook. |
| Material blog plugins | **Unsupported / explicitly deferred** | Blog index pages contain no post listing. Six post URLs move from Material's configured date/slug formats to source-path URLs; two blog archives, one personal archive, and one personal category page disappear. Blog and Personal were removed from migration scope by explicit decision on 2026-09-01; the manifest continues reporting the differences. |
| Privacy plugin | **Unsupported / replaced cleanly** | `theme.font: false` prevents hosted font requests in both builders. The obsolete plugin setting was removed, and validation now rejects third-party runtime assets in every generated HTML file. |
| Tags plugin | Partial | Post-level tag markup renders, but Material's generated `tags.json` is absent. Confirm the desired tag/search behavior with the eventual blog solution. |
| Production deployment | Not applicable yet | Zensical has no `gh-deploy` command. The later deployment phase must move to a static Pages artifact or an equivalent safe publisher. |

## Phase 2 compatibility audit and Phase 3 theme choice

The cleaned configuration passed `zensical build --clean --strict` and a live preview health check.

- All 97 ordinary page output paths match the Material baseline; the root index is also preserved.
- All 570 authored heading anchors match. Zensical adds one internal `#__skip` heading ID to a page without an authored H1.
- The generated link graph contains 6,896 checked local file/anchor references and all resolve. Zensical's generated `404.html` skip link still points to a missing `#__skip` target; that single exact upstream reference is excluded, while authored documentation receives no exception.
- Search contains 623 valid title/heading/body entries across heading levels 1–4. Every indexed location and anchor resolves, and representative Fragments, Security, `server-driven`, and `wire:model` queries have results.
- The eight configured top-level navigation sections render in order and Blog remains absent. Generated HTML contains the mobile drawer on all 107 HTML outputs, table-of-contents navigation on all 98 ordinary pages, 25 breadcrumb paths matching Material, and previous/next links on the expected 96 pages in each direction.
- Representative pages render highlighted code, inline code, admonitions, tables, attribute-list links and icons, macro-expanded includes, and custom HTML. Across ordinary pages the build contains 188 admonitions, 73 tables, and 280 highlighted code blocks.
- `CNAME`, sitemap, search data/worker, images, and modern theme assets are present.
- Legacy CSS, analytics overrides, footer social links, top navigation tabs, the auto-hiding header, and the Blog menu entry are absent as intentionally requested.

Both variants build successfully with the same ordinary page paths, heading count, and breadcrumb count. With hosted fonts enabled, classic declares Roboto/Roboto Mono while modern declares Inter/JetBrains Mono; their structural comparison still favored modern. The final configuration selects `theme.variant: modern` and sets `theme.font: false`, retaining the modern layout while using the system font stack without remote requests.

Automated browser attachment was unavailable, so viewport-specific layout, clicking the palette toggle, code-copy interaction, instant navigation, and typing into the search UI are not claimed as automated passes. They remain observable in the running local preview.

## Phase 4 native configuration decision

Keep `mkdocs.yml` as the only active configuration for this migration stage. Do not add `zensical.toml` yet.

This is a deliberate compatibility decision rather than unfinished conversion work:

- Zensical's current FAQ explicitly recommends that existing MkDocs projects do not switch to `zensical.toml` yet. Its compatibility documentation says automated conversion tooling will be provided later and that `mkdocs.yml` remains supported.
- Zensical 0.0.57 has `new`, `build`, and `serve` commands but no configuration converter. A manual translation would duplicate a large navigation tree without providing a functional benefit.
- The active YAML contains compatibility-specific values that are not a lossless one-to-one TOML edit: two instances of the `blog` plugin, Python-name emoji callbacks, and an MkDocs `hooks` entry. Zensical still requires external invocation for the hook and the deferred blog replacement remains unsettled; moving it while native module configuration is changing would mix configuration migration with feature migration.
- Both Material for MkDocs and Zensical currently consume the same file. Retaining it preserves the tested Material rollback path while Zensical's own compatibility layer performs the adaptation.
- If both files exist, Zensical 0.0.57 selects `zensical.toml` before `mkdocs.yml` by default. Keeping one authoritative file avoids accidental divergence and an unproven default-config switch.

Revisit native configuration after Zensical publishes conversion tooling or finalizes the relevant module configuration. At that point, add `zensical.toml` alongside `mkdocs.yml`, build each explicitly with `zensical build --config-file ...`, compare navigation, output paths, anchors, assets, and search, and remove YAML only after equivalence is proven. Until then the forward path is Zensical plus `mkdocs.yml`; rollback remains Material plus the same `mkdocs.yml`.

## Phase 5 GitHub Pages workflow

The migration branch replaces the legacy `mkdocs gh-deploy` job with separate build and deployment jobs in `.github/workflows/ci.yml`:

- Pull requests targeting `main` install the pinned `requirements.txt`, run `zensical build --config-file mkdocs.yml --clean --strict`, and validate representative outputs. They cannot upload or deploy a Pages artifact.
- Pushes to `main` run the same build and validation, then upload `site/` with `actions/upload-pages-artifact` and deploy it with `actions/deploy-pages`.
- Both the artifact upload step and the entire deployment job require `github.event_name == 'push'` and `github.ref == 'refs/heads/main'`.
- Workflow-wide permissions are read-only. Only the guarded deployment job receives `pages: write` and `id-token: write`, and it deploys through the protected `github-pages` environment.
- The build validates the root page, search data, representative Getting Started, Concepts, and Security pages, plus the exact `docs.magewirephp.nl` value copied into `site/CNAME`.
- Dependency and Zensical caches are intentionally omitted, following Zensical's current CI guidance while its caching implementation is changing.

The repository's live Pages configuration was inspected without modifying it. It currently uses legacy branch publishing from `gh-pages:/`; `docs.magewirephp.nl` is verified, its HTTPS certificate is approved through 2026-11-02, and HTTPS enforcement is currently disabled. The production site therefore remains on the existing Material output while this branch is under development.

GitHub Pages must be switched from `build_type: legacy` to `build_type: workflow` immediately before the final merge. This is deliberately not automated from the migration branch: `actions/configure-pages` cannot perform that transition using the normal `GITHUB_TOKEN`, and changing the repository setting now would disable the current `gh-pages` publishing path before cutover. After switching the source, merge to `main`, observe the Documentation workflow, and verify the custom domain and HTTPS response.

Rollback remains available because the new workflow does not delete or rewrite `gh-pages`. If artifact deployment fails at cutover, restore Pages to legacy publishing from `gh-pages:/`; the previously published Material site remains the rollback source.

## Phases 6–10 AI documentation layer

`scripts/generate_ai_docs.py` is the single implementation for both build paths. Zensical runs it as a post-build command; Material for MkDocs loads it through the existing `hooks` setting. The two paths were built independently and produced byte-identical AI outputs.

The generator reads `mkdocs.yml` and the canonical Markdown directly. It does not read or scrape generated HTML. It follows the real top-level navigation order, expands the repository's `include()` macro with literal-only argument parsing, removes Jinja `raw` controls that exist only for presentation, retains headings and code blocks, and adds source-document boundaries and canonical URLs.

The generated `site/` output contains:

```text
llms.txt
llms-full.txt
ai/getting-started.txt
ai/essentials.txt
ai/features.txt
ai/directives.txt
ai/concepts.txt
ai/theming.txt
ai/admin.txt
ai/advanced.txt
index.md
pages/**/*.md
```

The eight topic bundles are derived from the eight visible top-level navigation sections, not maintained as a second page list. The corpus and raw layer currently contain all 98 navigated Markdown documents. Blog and Personal sources remain excluded because they are not in the documentation navigation, and the deliberately unlisted Magewire Flakes draft remains excluded for the same reason.

`llms.txt` follows the llmstxt.org structure: one H1, a project summary blockquote, explanatory context, and H2 link-list sections. It links to the complete context, every topic bundle, and every navigated page's clean Markdown sibling. `llms-full.txt` contains the complete expanded navigated corpus, while each topic file contains the same source-derived content for its section.

Every AI output states `Magewire 3.x` as the documentation version and includes the same concise guardrail: do not assume Laravel Livewire APIs or behavior exist unless the Magewire documentation says so, and prefer the Magewire documentation when prior model knowledge conflicts.

The GitHub Actions build runs the generator after the strict Zensical build and validates the root AI files, representative topic bundles and raw Markdown pages, version, guardrail, CNAME, search data, and representative human documentation pages before an artifact can be uploaded. Generated AI files remain build artifacts under ignored `site/`; they are never maintained as duplicate source documents.

For a production-equivalent local preview, run the strict build, then the AI generator, then serve `site/` with a static file server. Starting `zensical serve` performs another Zensical build and does not invoke the external generator, so it is appropriate for live HTML editing but not by itself for checking the AI endpoints. Endpoint checks must inspect expected content because Zensical's preview fallback can return its 404 document with HTTP 200.

## Phase 11 raw Markdown URLs

Raw Markdown is implemented additively without changing Zensical routing. Each navigated `.html` page gains a clean, macro-expanded `.md` sibling at the same path:

```text
/pages/concepts/fragments.html  -> human documentation
/pages/concepts/fragments.md    -> clean Markdown
/index.html                     -> human documentation root
/index.md                       -> clean Markdown root
```

This matches the llmstxt.org v2 recommendation to replace `.html` with `.md`; `llms.txt` now points its page entries to those agent-friendly resources. The files preserve headings, code, authored links, and expanded includes without adding AI instructions to every individual document. Guardrails remain in `llms.txt`, `llms-full.txt`, and the topic bundles.

The initial proof generated 97 raw pages and kept all 107 then-existing HTML files byte-identical. After synchronizing the later CSP documentation from `main`, the same source-derived process generates 98 raw pages and 108 AI resources. Blog, Personal, and the unlisted Flakes draft remain outside the raw corpus by the same navigation rule used for the aggregate AI files.

No theme override was reintroduced solely to add HTML `<link rel="alternate">` metadata. Discovery through `llms.txt` provides the useful capability without adding template compatibility risk; alternate-link metadata can be reconsidered if Zensical exposes a native configuration mechanism.

Rollback is simply to stop emitting the `.md` siblings and rebuild cleanly. No existing route, redirect, source file, or Pages setting is changed.

## Phase 12 automated build validation

`scripts/validate_site.py` turns the compatibility proof into a repeatable, offline CI gate. The workflow runs it only after a clean strict Zensical build and AI generation, before any Pages artifact can be uploaded.

The validator derives the expected corpus and topic bundles from the real `mkdocs.yml` navigation, then verifies:

- every navigated human HTML page and raw Markdown sibling exists and is non-empty;
- the raw Markdown corpus and navigation-derived topic set contain no missing or unexpected files;
- `llms.txt` links to every navigated raw page, and every aggregate contains the configured Magewire version and AI guardrail;
- the custom domain, search index, root page, and representative Getting Started, Components, Directives, Fragments, Admin, Security, and Architecture URLs exist;
- every local `href` and `src` in all generated HTML resolves, including target anchors;
- no stylesheet, preconnect, script, image, or other runtime asset points at a third-party host;
- every local Markdown link, image, and embedded HTML reference in all 98 raw pages resolves, including target anchors;
- every search result location and anchor resolves to generated HTML, accepting both Zensical's `search.json` and Material's `search/search_index.json` rollback format.

The only excluded reference is Zensical 0.0.57's generated `404.html#__skip` link, already identified during Phase 2. The exception is exact and documented in code; authored documentation receives no exception.

A clean strict Zensical run validates 98 navigated pages, 108 HTML files, 6,896 HTML references, 317 raw Markdown references, 623 search entries, and 108 generated AI resources, with no third-party runtime assets. A clean strict Material rollback build validates 112 HTML files, 7,118 HTML references, 627 search entries, the same raw and AI resources, and the same zero-remote-assets condition. An intentional test with the Fragments HTML output removed failed on the required URL, incoming links, and search locations, confirming that the gate rejects an incomplete artifact.

The validator has no network dependency and does not modify the artifact, so it is deterministic in pull requests and cannot affect production. Rollback is limited to removing the validation command; the generated site and both build paths remain unchanged.

## Phase 13 production URL comparison

The production contract was captured from `https://docs.magewirephp.nl/sitemap.xml` on 2026-09-01 and cross-checked against the freshly fetched `origin/gh-pages` commit `ea2a9652b3c65bca644380465b0dece905c016b1`. The live response and published branch both provide the same 16,356-byte sitemap (`SHA-256 022281e5d01d5f0d3ac4332c3a9f5874f1faffbf55dad9f9bb7d78477d31cb7b`) generated from source commit `d48d6a2`.

That source commit was newer than the migration branch and added `pages/theming/csp-script-bootstrap.html`. Its Markdown source, navigation entry, and related links were synchronized into this branch before comparison, preventing a newly published ordinary documentation URL from being lost.

`tests/production-url-manifest.json` records all 111 sitemap URLs and all 707 published heading anchors. `scripts/compare_production_urls.py` compares that immutable baseline with the clean candidate artifact and its sitemap on every CI build. It requires exact case-sensitive `.html` paths, preserves every published heading anchor on compatible pages, and rejects unexpected URL loss, anchor loss, sitemap loss, stale exceptions, wrong sitemap origins, and sitemap entries without files.

Current comparison result:

- 101 of 111 production URLs are present at the same path;
- all heading anchors on ordinary documentation pages are preserved;
- 10 absent routes are the previously accepted Material-generated blog/personal permalinks and archive/category pages;
- 42 blog-index anchors and one personal-index anchor remain absent because Zensical does not render Material's post listings;
- the Blog index, Personal index, and deliberately unlisted Flakes page remain routable but are omitted from Zensical's navigation-derived sitemap;
- six Zensical source-path post URLs are candidate-only additions.

Every accepted difference is named with its reason in the manifest and is printed as a `DEFERRED` difference; no wildcard or blanket exclusion exists. These entries keep CI strict for the ordinary documentation while retaining an exact record if Blog or Personal is restored later.

The manifest is intentionally local and immutable during CI, so pull requests cannot redefine production by querying a changing live site. Refresh it only after deliberately publishing new production documentation or changing a recorded deferred decision, using the deployed sitemap and `gh-pages` artifact as dual evidence.

## URL comparison

The documentation pages represented by `index.md` and `docs/pages/**/*.md` preserve their existing `.html` paths. Blog-generated URLs do not.

Material-only blog/personal routes:

```text
blogs/2025/05/24/magewire-3---docs-publication.html
blogs/2025/06/02/magewire-3---hello-world.html
blogs/2025/09/08/magewire-3---beta-release.html
blogs/2025/11/13/magewire-3---a-different-kind-of-blog.html
blogs/2026/04/23/magewire-3---finally.html
blogs/archive/2025.html
blogs/archive/2026.html
personal/why-i-started-a-personal-corner.html
personal/archive/2026.html
personal/category/life.html
```

Zensical instead emits the six posts below and does not generate the archive/category pages:

```text
blogs/posts/a-different-kind-of-blog.html
blogs/posts/beta-release.html
blogs/posts/docs-publication.html
blogs/posts/hello-world.html
blogs/posts/magewire-version-three-release.html
personal/posts/first-post.html
```

Blog and Personal URL parity is explicitly deferred and is no longer a cutover condition. Their Markdown sources remain preserved, both sections remain absent from navigation, and the differences remain visible in the production manifest. Zensical's preview server returns its 404 document with HTTP 200 for unknown paths, so URL validation still compares generated files/content rather than relying on preview status codes.

## Phase 14 cleanup audit

The cleanup audit classifies legacy-looking files by active ownership before removal. Blog/Personal remain preserved for possible later restoration, so this phase performs only safe contraction.

Removed or already removed:

| Item | Reason |
| --- | --- |
| `docs/stylesheets/style.css` | Material-era selector overrides caused the reported Zensical styling problems and are no longer configured. |
| `overrides/partials/integrations/analytics/custom.html` | Empty analytics template; analytics configuration was removed and no template override remains. |
| `hooks/llms_txt.py` | Replaced by the tested dual-purpose `scripts/generate_ai_docs.py`; retaining two implementations would create drift. |
| Material `privacy` plugin setting | Zensical does not support it, system fonts remove the remote font dependency, and its implicit Mermaid download broke strict offline Material builds. Runtime-asset validation now enforces the desired outcome directly. |
| Tracked `__pycache__/main.cpython-311.pyc` and local bytecode caches | Generated interpreter artifacts with no runtime ownership; Python cache paths are now ignored. |
| Empty `hooks/`, `overrides/`, and `docs/stylesheets/` directories | No files or configuration still target them. |

Retained deliberately:

| Item | Current owner / removal condition |
| --- | --- |
| `mkdocs.yml` and `theme.name: material` | The tested Zensical compatibility entry point and the Material rollback configuration; retain until a native configuration migration is proven. |
| Material `blog` and `tags` plugin settings | Required by the production rollback. Blog and tags are deferred together and remain outside the Zensical cutover contract. |
| `hooks: scripts/generate_ai_docs.py` | Material rollback entry point for byte-identical AI outputs; Zensical invokes the same module explicitly in CI. |
| `main.py`, `includes/`, and `mkdocs-macros-plugin==1.5.0` | The canonical documentation uses 63 `include()` calls; the plugin remains necessary for Material rollback. |
| Explicit `PyYAML==6.0.3` | Direct runtime dependency of both AI generation and site validation, even though Zensical also depends on it transitively. |
| `Dockerfile` | Local Material rollback and comparison path. It now pins the verified `squidfunk/mkdocs-material:9.7.7` image and macros plugin instead of following floating releases. |
| Blog/personal `.authors.yml` files and avatar | Active Material blog metadata; needed until blog compatibility is replaced. |
| Existing images, including currently unreferenced logo/GIF assets | Already-published static paths may have external consumers; remove only after an asset URL audit or an explicit decision to retire them. |
| Unlisted Magewire Flakes Markdown | Its production HTML URL remains part of the captured contract even though it is intentionally outside navigation and AI context. |

The official Material image publishes an exact `9.7.7` tag, matching the version used for compatibility proof. Pinning it makes the rollback definition reproducible without changing Zensical output. The Docker image is for local preview/comparison only and is not used by the candidate Pages workflow.

No custom JavaScript, configured CSS, active template override, duplicate AI generator, obsolete deployment script, hosted font, or privacy-plugin dependency remains. Further deletion would remove an active rollback capability, a deliberately deferred blog input, or a published asset and is therefore deferred.

## Phase 15 cutover readiness

The canonical documentation content remains unchanged by the migration itself. Phase 13 only synchronized the newer CSP Markdown and links already published from `main`.

The migration is ready for the production cutover, subject only to the intentionally separate production actions:

1. Switch GitHub Pages from legacy branch publishing to GitHub Actions immediately before the final merge.
2. Merge the migration branch into `main` and observe the guarded Documentation workflow.
3. Verify the deployed custom domain, representative documentation URLs, search, and AI resources; if deployment fails, restore legacy publishing from `gh-pages:/`.

The full local gate passes with Zensical and the retained Material rollback path. Ordinary documentation URLs and anchors are preserved. The AI hook gap is resolved by the post-build generator. Privacy/offline behavior is resolved without third-party runtime requests. Blog and its tags behavior are explicitly deferred and are not a cutover blocker. Native TOML configuration remains a later upgrade, consistent with the Phase 4 decision.

Production is intentionally untouched: this branch does not deploy, the live Pages source remains the legacy `gh-pages` branch, and the final source-setting change and merge require an explicit cutover action.

## Forward and rollback paths

- Forward: keep `mkdocs.yml` and the Markdown tree stable, keep deferred blog differences explicit, switch Pages to GitHub Actions immediately before merge, and verify the deployment before retiring the rollback path.
- Rollback: the Material Dockerfile remains available with the previously verified versions pinned. Switching back to `main` restores the current production `mkdocs gh-deploy` workflow and published `gh-pages` branch. Only generated caches and already-replaced customizations have been contracted.

## Upstream references

- [Zensical compatibility](https://zensical.org/compatibility/)
- [Zensical configuration basics and unsupported settings](https://zensical.org/docs/setup/basics/)
- [Zensical plugin compatibility roadmap](https://zensical.org/compatibility/plugins/)
- [Zensical command-line differences](https://zensical.org/compatibility/cli/)
- [Zensical compatibility FAQ](https://zensical.org/docs/community/faqs/)
- [Zensical font configuration](https://zensical.org/docs/setup/fonts/)
- [Zensical data privacy guidance](https://zensical.org/docs/setup/data-privacy/)
