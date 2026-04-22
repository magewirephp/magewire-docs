# Alpine Loading

Magewire bundles the [CSP build of Alpine.js](https://alpinejs.dev/advanced/csp). A theme that loads Alpine itself will collide with Magewire's bundle and break directive registration.

## The rule

**Load Alpine exactly once. That one must be Magewire's bundle.**

If your theme ships an Alpine script tag:

```html
<!-- REMOVE this from your theme -->
<script src="…/alpine.min.js"></script>
```

…remove it. Magewire will load Alpine for you as part of its bundle.

## Why it matters

Alpine keeps a global store of directives, data components, and plugin registrations. A second instance instantiates its own store; directives registered against the first are invisible to the second, and vice versa. Typical symptoms:

- `x-data` blocks render their initial markup but never become reactive.
- `Alpine.store('theme')` exists from the theme's POV but not from Magewire's.
- `$wire.entangle()` resolves to `undefined`.

## Load-order considerations

Magewire renders the Alpine script in the `magewire.alpinejs.load` container. The container is placed in `<head>` by default, deferred with `defer` so it parses after the rest of the document is ready.

### Themes that need Alpine earlier

Hyvä expects Alpine to be available before its own setup scripts run. Move the block to an earlier container:

```xml title="view/frontend/layout/default_hyva.xml"
<move element="magewire.alpinejs.load" destination="head.additional" before="-" />
```

### Themes that inject scripts above Magewire

The theme loads its bundle into `<head>` synchronously; Magewire's deferred script hasn't parsed yet when the theme's `x-data` attributes render. Two options:

1. Move `magewire.alpinejs.load` to a container the theme's script depends on.
2. Keep theme scripts in `<body>` after the Magewire container.

## Initialisation events

| Event | Use |
|---|---|
| `alpine:init` | Register `Alpine.data()`, `Alpine.store()`, `Alpine.bind()`, utilities, addons |
| `magewire:init` | Register Magewire hooks (commit, request, morph) |
| `magewire:initialized` | Register custom `Magewire.directive()`s |

Always guard with `{ once: true }` — SPA-style navigation can re-fire initialisation events and duplicate registrations throw.

```html
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('myBlock', () => ({ open: false }));
    }, { once: true });
</script>
```

## Debugging double-load

Paste into the browser console:

```javascript
Alpine.version
```

Magewire's bundle uses a specific version — a mismatch or `undefined` points at a second Alpine overwriting Magewire's. View-source-search for `alpine` / `Alpine` across all script tags; there should be exactly one.

## Related

- [Alpine](../features/alpine.md) — directive surface.
- [Layout containers](layout-containers.md) — the target of `<move>` and `<referenceContainer>`.
- [Fragments](../concepts/fragments.md) — CSP-safe inline scripts.
