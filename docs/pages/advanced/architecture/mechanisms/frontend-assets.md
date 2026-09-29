# FrontendAssets

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

`FrontendAssets` (sort order `1400`) is a late mechanism that boots before `HandleCompiling` at `1500`. It is responsible for
getting Magewire's **JavaScript runtime** onto the page, together with the script attributes the runtime needs to boot.
Magewire's styles do not pass through this mechanism; they load as a layout head asset (see
[Core styles](../../../theming/styles.md)).

## What it emits

- **The JS runtime**: the Magewire/Livewire bundle, served as a Magento static asset. The script
  route resolves the bundle through Magento's asset repository (`returnJavaScriptAsFile()`), so it
  honours secure/insecure base URLs and Magento's static file handling.
- **No styles**: the ported mechanism keeps Livewire's `styles()` method, but Magewire does not call it. The
  stylesheet is added by `src/view/base/layout/default.xml`.
- **The script config**: the bootstrap data the runtime reads on load (including the
  `/magewire/update` URI and CSP nonces).
- **The source map**: `maps()` serves the bundle's `.map` file for debugging.

It tracks `hasRenderedScripts` / `hasRenderedStyles` so the payload is emitted once per page, and
resets those flags on the `flush-state` event.

## Where it surfaces in layout

`FrontendAssets` ships a `FrontendAssetsViewModel` with two methods: `getScriptPath()` returns the bundle URL, and
`getScriptAttributes()` renders the `script.html_attributes` configured in area DI. Theme packages use it to print the
Magewire `<script>` tag into `magewire.alpinejs.load`. The container tree and how to reorder or swap the bundle are
documented on the [Layout](../layout.md) page (see `magewire.alpinejs.load` and `magewire.priority`).

CSP nonces for the emitted tags come from the same source as the
[`utils()->csp()`](../../../essentials/view-model.md) helper, so inline Magewire scripts stay
CSP-compliant.

## Related

- [Portman](../portman.md): the supported public PHP porting workflow. JavaScript release assembly is maintainer-only.
- [Mechanisms](index.md): the pipeline overview.
- [Layout](../layout.md): the containers these assets render into.
- [View Model & Utilities](../../../essentials/view-model.md): `utils()->magewire()->getUpdateUri()` and `utils()->csp()`.
- [Alpine loading](../../../theming/alpine-loading.md): coordinating Alpine with the bundle.
