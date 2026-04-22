# Layout Containers

Magewire emits its runtime as a layout tree of named containers and blocks. Theme modules extend Magewire by adding blocks to these containers — never by replacing Magewire's core layout files.

## Full reference

| Container / block | Kind | What goes here |
|---|---|---|
| `magewire.alpinejs.load` | container | The Alpine bundle script tag. Reorder here if you need Alpine loaded at a different point (e.g. Hyvä's early-head requirement). |
| `magewire.alpinejs` | container | Global `$wire` setup, Alpine stores registered under `Alpine.store()`. |
| `magewire.alpinejs.components` | container | Reusable Alpine components (`Alpine.data()`). |
| `magewire.utilities` | block | Pure helper functions registered on `window.MagewireUtilities`. Children render inside. |
| `magewire.addons` | block | Stateful plugins registered on `window.MagewireAddons`. Children render inside. |
| `magewire.before` | container | User directives, theme-scoped UI components, custom `wire:*` directives — anything that must run before Magewire initialises. |
| `magewire.internal.backwards-compatibility` | container | V1 BC shims — hook aliases, `wire:model` rewriting, entangle proxy. Owned by the BC Feature. |
| `magewire.directives` | block | Custom `Magewire.directive()` registrations. Children render inside. |
| `magewire.features` | block | Feature bridge scripts — one child per registered Feature. Children render inside. |
| `magewire.after` | container | Last-to-render theme content. Theme flourishes, late-bound overrides. |
| `magewire.ui-components` | container | Alpine UI components shipped by Magewire (the notifier lives here). |
| `magewire.script` | block | The core Magewire library `<script>` tag. |

## Container vs. block

**Container** (`<referenceContainer>`) is additive. Your block is added alongside Magewire's existing children. Use containers for extension.

**Block** (`<referenceBlock>`) replaces. The target's template and arguments are overwritten by your declaration. Use blocks only when you explicitly need to replace a Magewire-provided block — which is rare.

```xml
<!-- Right: additive -->
<referenceContainer name="magewire.features">
    <block name="magewire.features.my-bridge"
           template="Vendor_Mine::magewire-features/my-bridge.phtml" />
</referenceContainer>

<!-- Wrong in most cases: replaces the core block -->
<referenceBlock name="magewire.script"
                template="Vendor_Mine::different-script.phtml" />
```

## Ordering children

Children within a container inherit Magento's usual ordering primitives — `before`, `after`, and `sortOrder`. Use them when a feature must run before or after another:

```xml
<referenceContainer name="magewire.features">
    <block name="magewire.features.a" template="…" before="-" />          <!-- first -->
    <block name="magewire.features.b" template="…" />
    <block name="magewire.features.c" template="…" after="magewire.features.b" />
</referenceContainer>
```

## Where to render what

| Kind of asset | Container |
|---|---|
| Feature bridge script | `magewire.features` |
| Stateful JS plugin (auto-save, analytics) | `magewire.addons` |
| Pure helper (formatters, translators) | `magewire.utilities` |
| Reusable Alpine component | `magewire.alpinejs.components` |
| Alpine store (global reactive state) | `magewire.alpinejs` |
| Custom `wire:*` directive | `magewire.directives` |
| Pre-initialisation UI | `magewire.before` |
| Post-initialisation UI | `magewire.after` |
| Alpine UI widgets (notifier, modals) | `magewire.ui-components` |

## Anti-patterns

- Using `<referenceBlock>` on a container name — it silently fails.
- Adding raw `<script>` tags inside a container — use a fragment template for CSP.
- Hard-coding an existing sibling's block name into `after=""` without declaring a dependency — if the sibling is removed, your ordering silently breaks. Prefer `sortOrder`.
- Adding blocks to Magewire's containers from global `etc/layout/` — always use an area-scoped layout handle (`default_{theme}.xml` or `adminhtml_default.xml`).

## Related

- [Compatibility module](compatibility-module.md)
- [Alpine loading](alpine-loading.md) — concrete use of `magewire.alpinejs.load`.
- [JavaScript](../advanced/javascript/index.md) — utilities, addons, directives, components in depth.
