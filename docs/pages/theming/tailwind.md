# Tailwind

Tailwind integration belongs to the theme package. Magewire core does not require every installation to scan a conventional `view/frontend/tailwind/` tree.

## Hyvä package

The current `magewirephp/magewire-hyva-theme` package provides a Tailwind source file for Hyvä. Its source registration scans the package's `src/view` tree and imports the notifier styles shipped by that package.

Install the package and include its Hyvä Tailwind source through the mechanism supported by the installed Hyvä version. Use the package source as the authoritative path:

```css
@source "../../../../../src/view";
```

The relative path is evaluated from the package's Tailwind source file; do not paste it into an unrelated theme unchanged. Resolve paths from the consuming stylesheet and verify them during the Tailwind build.

## Custom Tailwind integrations

Scan only packages that contain templates or JavaScript with classes needed by the storefront. In particular:

- core templates are below `vendor/magewirephp/magewire/src/view`;
- Hyvä integration templates are below `vendor/magewirephp/magewire-hyva-theme/src/view`;
- other companion packages may have different trees and should not be added speculatively.

Magewire does not currently publish the `--notifier-*` and `--wire-loading-spinner` custom-property contract previously shown in these docs. Style the rendered markup through the CSS shipped by the compatibility package or an explicit theme override, and recheck selectors after package upgrades.

Magento admin does not use this storefront Tailwind integration. See [Admin](../admin/index.md).
