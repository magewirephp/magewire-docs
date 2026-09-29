<a id="theming"></a>
<a id="three-layers"></a>

# Themes and Magewire

Magewire components can render through any Magento theme. The component PHP
class and its actions stay the same; a theme integration supplies the browser
loading, layout, CSS, and any theme-specific bridges. Since Magewire 3.7, core
ships framework-independent styles for its own UI that a theme can adjust; see
[Core styles](styles.md).

<a id="supported-themes"></a>

## Hyvä storefront

Install the maintained Hyvä integration alongside Magewire:

```shell
composer require magewirephp/magewire magewirephp/magewire-hyva-theme
bin/magento module:enable Magewirephp_Magewire Magewirephp_MagewireHyvaTheme
bin/magento setup:upgrade
```

Package 3.1.2 requires Magewire 3.7. Magewire's own UI is styled without a
Tailwind build. To use the package's optional Hyvä notifier presentation,
rebuild the theme after `setup:upgrade`; see [Tailwind](tailwind.md). The
integration coordinates Magewire's bundled Alpine with Hyvä's normal Alpine
loader and includes the flash-message bridge.
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

It supplies legacy browser shims. Since package 3.1.0, which requires
Magewire 3.7, components inside the checkout's main container receive BC by
default. New V3 components should use current directives, events, and
lifecycle hooks, and opt out with
`#[HandleBackwardsCompatibility(enabled: false)]`.

### Hyvä Checkout flash messages

Since package 3.1.0, consecutive checkout flash messages with the same text
and type are shown once, with a count badge. The package wraps Hyvä's
`initMessages` component rather than replacing its template, so it only
applies on the checkout page and only when Hyvä's message component is
present:

- messages rendered on page load are grouped when neighbouring messages match;
- a new message that matches the last visible one increments its count
  instead of being added again;
- messages with empty text are never grouped, and the counts reset once the
  message list is empty;
- the badge appears from two occurrences and is emphasized above ten, like the
  [notifier badge](../advanced/javascript/addons/magewire-notifier.md#repeated-messages).

Grouping is enabled by default. Turn it off with the **Group Consecutive
Messages** field of the checkout's **Flash Messages** configuration group
(`hyva_themes_checkout/component/flash_messages/group_consecutive`), per
website or store view. The badge styles are compiled into the Hyvä theme, so
rebuild the theme after installing or updating the package; see
[Tailwind](tailwind.md#hyva-checkout-package).

## Breeze storefront

For an enabled Breeze storefront, install the
[`swissup/module-breeze-magewire`](breeze.md) integration. It supplies the
`breeze_default` layout bridge, Magewire runtime host, flash-message listener,
and scroll-reveal morph handling. Keep your reusable component logic in its
feature module; add a Breeze-only companion module only for extra theme
behavior. The [Breeze guide](breeze.md) includes installation, a component,
and a small extension example.

<a id="when-you-need-a-theme-module"></a>

## Another storefront theme

For Luma or a custom theme without an integration package, build a
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
