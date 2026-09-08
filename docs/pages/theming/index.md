# Theming

Magewire is not tied to a single Magento theme. Most active theme integration belongs in **theme compatibility modules**
for Hyvä, Luma, Breeze, or a custom theme. Magento Admin support is an area integration rather than a storefront theme.

This section explains how the theming layer is organised and how to build a compatibility module for your own theme.

## Three layers

Magewire is deliberately split across three layers:

| Layer | Location | Responsibility |
|---|---|---|
| **Core module** | `magewirephp/magewire` | Framework runtime. Controllers, DI, events, layout XML scaffolding, and templates. Magewire 3.6 still contains a legacy Hyvä build-config observer that has not yet moved out. |
| **Global view layer** | `magewirephp/magewire/src/view/base/` + `src/view/frontend/` | Skeleton every theme inherits: named layout nodes for JS addons, utilities, Alpine components, directives, and feature bridges. |
| **Integration packages** | Standalone packages like `magewirephp/magewire-hyva-theme`, `magewirephp/magewire-hyva-checkout`, and `magewirephp/magewire-admin` | Adapts Magewire to a storefront theme, checkout implementation, or admin area through the integration pieces it needs. |

The split matters because **every theme has different conventions**. Hyvä uses Tailwind and its own `hyva_config_generate_before` event for build hooks. Luma uses LESS. The admin uses RequireJS. A core runtime that tried to handle all of them would be unreadable; a thin core with per-theme adapters is tractable.

## Supported themes

!!! info "Themes are separate packages since 3.2.0"
    Before 3.2.0 the Hyvä theme and the admin marker shipped in-tree under a `themes/` directory inside the core
    `magewirephp/magewire` repository. That directory no longer exists. Maintained first-party integrations now have
    their own repositories and Composer packages. Core 3.6 still contains a legacy
    `HyvaConfigGenerateBefore` observer, so the source split is not yet completely theme-neutral.

| Theme | Package | Install |
|---|---|---|
| **Hyvä** | `magewirephp/magewire-hyva-theme` | `composer require magewirephp/magewire-hyva-theme` |
| **Hyvä Checkout** | `magewirephp/magewire-hyva-checkout` | `composer require magewirephp/magewire-hyva-checkout` |
| **Magento Admin** | `magewirephp/magewire-admin` | `composer require magewirephp/magewire-admin` |
| Luma | custom/community integration required | No maintained first-party Magewire 3 package. |
| Breeze | custom/community integration required | No maintained first-party Magewire 3 package. |

Each package carries only the integration pieces it needs, such as layout overrides, event observers, routes, plugins,
or CSS build configuration. These responsibilities are not identical across packages. See
[Admin](../admin/index.md) for the separate admin-area integration.

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

- [Compatibility module](compatibility-module.md): build one from scratch.
- [Layout containers](layout-containers.md): the extension points you plug into.
- [Alpine loading](alpine-loading.md): coordinate the theme and Magewire Alpine loaders.
- [Hyvä CSP script bootstrap](csp-script-bootstrap.md): load runtime request configuration without Alpine directives on the script element.
- [Tailwind](tailwind.md): integrate Magewire's components into a Tailwind pipeline.
- [Backwards compatibility](../essentials/backwards-compatibility.md): V1 → V3 BC system.
- [Hyvä Checkout BC](hyva-checkout-bc.md): explicit BC opt-in and the current container-fallback limitation.
