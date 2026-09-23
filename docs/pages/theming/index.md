<a id="theming"></a>
<a id="three-layers"></a>

# Themes and Magewire

Magewire components can render through any Magento theme. The component PHP
class and its actions stay the same; a theme integration supplies the browser
loading, layout, CSS, and any theme-specific bridges.

<a id="supported-themes"></a>

## Hyvä storefront

Install the maintained Hyvä integration alongside Magewire:

```shell
composer require magewirephp/magewire magewirephp/magewire-hyva-theme
bin/magento module:enable Magewirephp_Magewire Magewirephp_MagewireHyvaTheme
bin/magento setup:upgrade
```

Rebuild your Hyvä theme assets after installation so its Tailwind build sees
the package's styles. The integration coordinates Magewire's bundled Alpine
with Hyvä's normal Alpine loader and includes the flash-message bridge.
Follow [Alpine loading](alpine-loading.md) if you need to inspect that
decision.

Use the same component class with a different template when the theme calls
for different markup:

```xml title="view/frontend/layout/catalog_product_view.xml"
<referenceBlock name="vendor.module.product-options"
                template="Vendor_HyvaIntegration::magewire/product-options.phtml"/>
```

The layout block keeps its `magewire` argument and PHP class. The theme
module changes only the template. This makes the business behavior reusable
across storefronts. See [Components](../essentials/components.md) for the
original block binding.

## Existing Hyvä Checkout components

If an installed Hyvä Checkout integration still uses Magewire V1 behavior,
add the [Hyvä Checkout compatibility package](hyva-checkout-bc.md) during
migration:

```shell
composer require magewirephp/magewire-hyva-checkout
bin/magento module:enable Magewirephp_MagewireHyvaCheckout
bin/magento setup:upgrade
```

It supplies legacy browser shims. New V3 components should use current
directives, events, and lifecycle hooks instead of depending on those shims.

<a id="when-you-need-a-theme-module"></a>

## Another storefront theme

For Luma, Breeze, or a custom theme, build a
[compatibility module](compatibility-module.md). Give it ownership of the
theme's script loading and browser bridges. Keep component state, actions,
and persistence in the feature module. Start with Magewire's
[layout nodes](layout-containers.md); use the actual theme layout handles
and asset pipeline rather than assuming Hyvä's handles apply everywhere.

Magento Admin has its own
[integration package](../admin/installation.md) and area-specific layout.

<a id="where-to-go-next"></a>

## Related

- [Compatibility module](compatibility-module.md): a complete package example.
- [Layout nodes](layout-containers.md): safe extension points.
- [Tailwind](tailwind.md): scan the right package sources.
- [CSP script bootstrap](csp-script-bootstrap.md): how Hyvä receives runtime configuration.
