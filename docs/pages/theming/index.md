# Theming

Magewire is not tied to a single Magento theme. The core package ships a theme-agnostic runtime; **theme compatibility modules** adapt that runtime to Hyvä, Luma, Breeze, the admin, or a custom theme.

This section explains how the theming layer is organised and how to build a compatibility module for your own theme.

## Three layers

Magewire is deliberately split across three layers:

| Layer | Location | Responsibility |
|---|---|---|
| **Core module** | `magewirephp/magewire` | Framework runtime. Controllers, DI, events, layout XML scaffolding, templates. Theme-agnostic. |
| **Global view layer** | `magewirephp/magewire/src/view/base/` + `src/view/frontend/` | Skeleton every theme inherits — named layout containers for JS addons, utilities, Alpine components, directives, Features. |
| **Theme compatibility modules** | `magewirephp/magewire/themes/{Theme}/` (in-tree) or standalone packages like `magewirephp/magewire-admin` | Adapts Magewire to one theme — layout overrides, Features, CSS pipeline, BC layers. |

The split matters because **every theme has different conventions**. Hyvä uses Tailwind and its own `hyva_config_generate_before` event for build hooks. Luma uses LESS. The admin uses RequireJS. A core runtime that tried to handle all of them would be unreadable; a thin core with per-theme adapters is tractable.

## Supported themes

| Theme | Location | Install |
|---|---|---|
| **Hyvä** | in-tree (`themes/Hyva/`) | Installed with the core `magewirephp/magewire` package |
| **Magento Admin** | standalone (`magewirephp/magewire-admin`) | `composer require magewirephp/magewire-admin` |
| Luma | community | _Not supported in V3 at launch_ |
| Breeze | community | _Not supported in V3 at launch_ |

Hyvä ships in-tree because it is the theme Magewire is developed against. The admin ships standalone because it ships its own controllers, routes, and plugins — see [Admin](../admin/index.md).

## When you need a theme module

Install Magewire's core package without a theme module and you get:

- A working `/magewire/update` route.
- The JS bundle (including Alpine CSP).
- Named layout containers to extend.

You will still need a theme module whenever you want:

- Theme-specific layout overrides (Alpine loading order, script injection point).
- Theme-scoped Features (flash-message bridges, BC layers, custom wire directives).
- CSS pipeline integration (Tailwind `@source`, build-hook observers).
- Backwards-compatibility shims for V1 components in an existing theme.

## Where to go next

- [Compatibility module](compatibility-module.md) — build one from scratch.
- [Layout containers](layout-containers.md) — the extension points you plug into.
- [Alpine loading](alpine-loading.md) — remove your theme's own Alpine, fix load order.
- [Tailwind](tailwind.md) — integrate Magewire's components into a Tailwind pipeline.
- [Backwards compatibility](backwards-compatibility.md) — V1 → V3 BC system.
- [Hyvä Checkout BC](hyva-checkout-bc.md) — Hyvä-specific auto-enabled BC.
