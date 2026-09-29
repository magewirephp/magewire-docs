# Tailwind

Tailwind integration belongs to the theme package. Since Magewire 3.7, core needs no Tailwind build: its templates
contain no utility classes, and it ships its own stylesheet (see [Core styles](styles.md)). A theme package can add
a presentation that follows the theme's Tailwind palette on top.

## Hyvä package

`magewirephp/magewire-hyva-theme` 3.1.2, which requires Magewire 3.7, adds an optional Hyvä presentation for the
notifier. Until the theme is rebuilt with the package's sources, the notifier uses the core styles.

### How the package reaches the Hyvä build

The package observes `hyva_config_generate_before` and adds itself, and only itself, to `app/etc/hyva-themes.json`.
Hyvä regenerates that file during `bin/magento setup:upgrade` and when modules are enabled or disabled. Run
`bin/magento hyva:config:generate` to regenerate it on demand.

Up to package 3.1.1, the observer registered Magewire core as well, and core 3.6 had its own observer and Tailwind
config. Magewire 3.7 removed both, so core is no longer part of the Hyvä build.

The Hyvä build reads these files from the package's `src/view/frontend/tailwind/` directory:

| File | Read by | Contents |
|---|---|---|
| `module.css` | Tailwind v4 themes | `@source` globs for the package's layout XML and templates, then `notifier-v4.css` and `notifier.css` |
| `tailwind.config.js` | Tailwind v3 themes | `content` globs for the package's layout XML and templates |
| `tailwind-source.css` | Tailwind v3 themes | `notifier-v3.css`, then `notifier.css` |

`notifier-v3.css` and `notifier-v4.css` declare the same tokens from theme values, with `theme("colors.gray.100")` in
v3 and `var(--color-gray-100)` in v4. `notifier.css` is plain CSS shared by both.

### Notifier presentation

The Hyvä layer keeps core's layout: position, width, offset, and gap still come from the core
`--magewire-notifier-*` tokens. It changes the look of each notification:

- no accent stripe; typed notifications get a 2px border in the type color and a tinted surface;
- bold text on the theme's gray surface with a larger shadow;
- a badge surface that matches the notification type;
- close-button colors from the theme palette.

Its selectors target `.magewire-notifier .magewire-notifier-item.message[data-type]`, the markup core renders since
3.7.0.

### Hyvä notifier tokens

The tokens are declared on `.magewire-notifier`, so override them on that selector:

| Token | Tailwind v3 | Tailwind v4 |
|---|---|---|
| `--magewire-hyva-notifier-radius` | `borderRadius.DEFAULT` | `--radius-sm` |
| `--magewire-hyva-notifier-surface` | `colors.gray.100` | `--color-gray-100` |
| `--magewire-hyva-notifier-color` | `colors.black` | `--color-black` |
| `--magewire-hyva-notifier-shadow` | `boxShadow.xl` | `--shadow-xl` |
| `--magewire-hyva-notifier-occurrences-surface` | `colors.gray.500` | `--color-gray-500` |
| `--magewire-hyva-notifier-occurrences-shadow` | `boxShadow.md` | `--shadow-md` |
| `--magewire-hyva-notifier-close-color` | `colors.gray.600` | `--color-gray-600` |
| `--magewire-hyva-notifier-close-hover-color` | `colors.black` | `--color-black` |
| `--magewire-hyva-notifier-{type}-border` | `colors.{color}.500` | `--color-{color}-500` |
| `--magewire-hyva-notifier-{type}-surface` | `colors.{color}.50` | `--color-{color}-50` |

`{type}` is `success` (green), `info` (blue, also used for `notice`), `warning` (yellow), or `error` (red).

```css title="web/tailwind/tailwind-source.css (Tailwind v4 theme)"
.magewire-notifier {
    --magewire-hyva-notifier-surface: var(--color-white);
    --magewire-hyva-notifier-error-border: var(--color-rose-600);
}
```

### Rebuild after installing or updating

```shell
bin/magento setup:upgrade
cd app/design/frontend/<Vendor>/<theme>/web/tailwind
npm run build
```

`setup:upgrade` regenerates `app/etc/hyva-themes.json`, and the build compiles the package's sources into the theme
CSS. The compiled theme CSS keeps the rules from the previous build until you rebuild.

### Upgrading from package 3.1.1

- Upgrade Magewire to 3.7 together with the package.
- The package no longer positions the notifier. Its `--offset`, `--index`, and `--gap` properties were removed; set
  `--magewire-notifier-offset`, `--magewire-notifier-z-index`, and `--magewire-notifier-gap` on `.magewire-notifier`
  instead.
- Rebuild the theme so the new selectors and tokens replace the compiled 3.1.1 rules.
- A module that overrides core Magewire templates with Tailwind utility classes must register itself for the Hyvä
  build, because core templates are no longer scanned.

## Hyvä Checkout package

`magewirephp/magewire-hyva-checkout` 3.1.0 and later registers itself for the Hyvä build in the same way and ships
`module.css` (Tailwind v4) and `tailwind-source.css` with `tailwind.config.js` (Tailwind v3). Both import
`components/flash-message-occurrences.css`, which styles the count badge on grouped checkout flash messages with the
theme's utilities. Rebuild the theme after installing or updating the package. See
[Hyvä Checkout flash messages](index.md#hyva-checkout-flash-messages) for the grouping behavior.

## Custom Tailwind integrations

Scan only packages that contain templates or JavaScript with classes needed by the storefront:

- Magewire core templates need no scanning since 3.7;
- the Hyvä and Hyvä Checkout packages register their own sources through `hyva-themes.json`;
- other companion packages may have different trees and should not be added speculatively.

For themes without Tailwind, the core stylesheet and its `--magewire-*` tokens are the styling contract. See
[Core styles](styles.md).

Magento admin does not use this storefront Tailwind integration. See [Admin](../admin/index.md).
