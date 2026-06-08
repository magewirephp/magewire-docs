# FrontendAssets

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

`FrontendAssets` (sort order `1400`) is the last mechanism in the pipeline. It's responsible for
getting Magewire's **client-side payload** onto the page — the JavaScript runtime, the supporting
styles, and the per-page configuration the runtime needs to boot.

## What it emits

- **The JS runtime** — the Magewire/Livewire bundle, served as a Magento static asset. The script
  route resolves the bundle through Magento's asset repository (`returnJavaScriptAsFile()`), so it
  honours secure/insecure base URLs and Magento's static file handling.
- **The styles** — the small stylesheet that hides `wire:loading` elements until a request is in
  flight (and the related loading-state selectors).
- **The script config** — the bootstrap data the runtime reads on load (including the
  `/magewire/update` URI and CSP nonces).
- **The source map** — `maps()` serves the bundle's `.map` file for debugging.

It tracks `hasRenderedScripts` / `hasRenderedStyles` so the payload is emitted once per page, and
resets those flags on the `flush-state` event.

## Where it surfaces in layout

`FrontendAssets` ships a `FrontendAssetsViewModel` that the layout uses to render these pieces into
the right containers — the `<script>` tag, the `magewire.css` styles block, and the early
`magewire.priority` setup. The container tree and how to reorder or swap the bundle are documented on
the [Layout](../layout.md) page (see `magewire.alpinejs.load`, `magewire.css`, and
`magewire.priority`).

CSP nonces for the emitted tags come from the same source as the
[`utils()->csp()`](../../../essentials/view-model.md) helper, so inline Magewire scripts stay
CSP-compliant.

## Related

- [Mechanisms](index.md) — the pipeline overview.
- [Layout](../layout.md) — the containers these assets render into.
- [View Model & Utilities](../../../essentials/view-model.md) — `utils()->magewire()->getUpdateUri()` and `utils()->csp()`.
- [Alpine loading](../../../theming/alpine-loading.md) — coordinating Alpine with the bundle.