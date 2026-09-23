# Alpine Loading

Magewire's browser build includes Alpine.js. A theme integration must ensure that only one Alpine runtime starts while preserving the theme's behavior on pages where Magewire is absent.

## Hyvä

Install `magewirephp/magewire-hyva-theme` instead of manually removing Hyvä's Alpine block. The package wraps Hyvä's loader:

- pages with Magewire components use Magewire's bundled Alpine runtime;
- pages without Magewire components can fall back to Hyvä's Alpine runtime.

This conditional behavior is why a global layout removal of Hyvä's Alpine asset is incorrect.

See [Hyvä CSP Script Bootstrap](csp-script-bootstrap.md) for the runtime
configuration carrier, lifecycle ordering, and extension points used on
component pages.

```shell
composer require magewirephp/magewire-hyva-theme
bin/magento module:enable Magewirephp_MagewireHyvaTheme
bin/magento setup:upgrade
```

## Breeze

Install [`swissup/module-breeze-magewire`](breeze.md) on a Breeze storefront.
Its `breeze_default` layout loads the Magewire script and runtime host on
component pages. Do not copy Hyvä's `default_hyva` layout or add a second
Magewire script to the page. The [Breeze guide](breeze.md) covers installation
and the checks for pages with and without components.

## Custom themes

A custom compatibility module owns three decisions:

1. where the Magewire loader is rendered;
2. how the theme's existing Alpine asset is suppressed on Magewire pages;
3. how the theme loads Alpine when the page has no Magewire components.

Use the `magewire.alpinejs.load` layout node as the integration point. Preserve script ordering expected by the theme and test pages both with and without components.

## Initialization events

| Event | Use |
|---|---|
| `alpine:init` | Register `Alpine.data()`, stores, binds, and Alpine-dependent registries. |
| `magewire:init` | Register Magewire hooks. |
| `magewire:initialized` | Run work that requires the initialized runtime. |

```php title="view/frontend/templates/js/magewire/search-box.phtml"
<?php $script = $block->getData('view_model')->utils()->fragment()->make()->script()->start() ?>
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('searchBox', () => ({ open: false }))
    }, { once: true })
</script>
<?php $script->end() ?>
```

If Alpine warns that it was started more than once, inspect the final merged layout and rendered script tags before changing component code.
