# Tailwind

Magewire ships CSS classes for its built-in UI components (the notifier, default wire-loading indicators, BC-layer utilities). If your theme uses Tailwind, those classes need to be visible to Tailwind's content scanner or they will be purged from the final CSS.

## Magewire's source paths

Every Magewire package and compatibility module keeps its Tailwind-scannable templates under `view/frontend/tailwind/` — a convention inherited from Hyvä. Tailwind configs in the theme should include these directories as `@source` inputs.

## Hyvä integration (automatic)

When the Hyvä compatibility module is installed, Magewire hooks Hyvä's build pipeline via the `hyva_config_generate_before` observer event. An observer registers every Magewire module path that contains `view/frontend/tailwind/` into Hyvä's content-sources list, so Tailwind scans them automatically.

You do not need to configure anything for Hyvä beyond installing Magewire's core and (optionally) installing additional compatibility modules.

## Custom Tailwind themes

For a non-Hyvä Tailwind theme, add Magewire's tailwind paths to your theme's `tailwind.config.js`:

```javascript title="view/frontend/web/tailwind/tailwind.config.js"
module.exports = {
    content: [
        '../../../**/*.phtml',
        '../../../vendor/magewirephp/magewire/src/view/*/tailwind/**/*.{phtml,html,js}',
        '../../../vendor/magewirephp/magewire/themes/*/view/*/tailwind/**/*.{phtml,html,js}',
        // add per-package paths for standalone compat modules:
        '../../../vendor/magewirephp/magewire-admin/view/*/tailwind/**/*.{phtml,html,js}',
    ],
    // …
};
```

Relative paths depend on where your config lives. Adjust the prefix.

## CSS variables for theming

Magewire components use CSS custom properties for colours and spacing so themes can override without rewriting selectors. Document set per component:

| Variable | Default | Used in |
|---|---|---|
| `--notifier-bg` | theme-default | Notifier toast backgrounds |
| `--notifier-text` | theme-default | Notifier toast text |
| `--notifier-radius` | `0.5rem` | Notifier corner radius |
| `--wire-loading-spinner` | theme-default | Default spinner colour |

Override in your theme's CSS:

```css title="view/frontend/web/css/_magewire-overrides.css"
:root {
    --notifier-bg: #111;
    --notifier-text: #fff;
    --notifier-radius: 0;
}
```

(Exact variable set depends on the Magewire release — consult the core `themes/Hyva/view/frontend/tailwind/` tree for the current list.)

## No Tailwind in admin

The Magento admin theme does **not** use Tailwind. `magewire-admin` targets the admin's own stylesheet conventions — no `@source` configuration is needed. See [Admin](../admin/index.md).

## Related

- [Compatibility module](compatibility-module.md)
- [Layout containers](layout-containers.md)
