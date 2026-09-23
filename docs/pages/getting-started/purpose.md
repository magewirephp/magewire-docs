# Why Magewire?

Suppose a Magento block needs to respond to a customer without reloading the
page. You can keep the layout, PHTML template, dependency injection, and
business services you already use. Magewire adds a PHP component for the
state and actions, then updates that block in the browser.

Use it for interactions that repeatedly need the server: product selectors,
account forms, cart tools, checkout steps, and admin editors. For static
output, an ordinary Magento block is simpler. For a disclosure or tab that
only changes browser state, Alpine is enough.

## More than a port

Magewire 3 brings selected Livewire 3 concepts into Magento. Magento still
owns its routes, layout, templates, repositories, and authorization. Magewire
adds component snapshots, actions, lifecycle hooks, and directives where they
fit those conventions.

That division makes a feature easy to find: the PHP component handles the
interaction, a Magento service handles business rules, and the layout decides
where it appears.

<a id="shake-things-up"></a>

## Build for reuse

Pass page-specific values through layout instead of hard-coding them into a
component class:

```xml
<block name="vendor.catalog.featured" template="Vendor_Module::magewire/product-list.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object" shared="false">Vendor\Module\Magewire\ProductList</argument>
        <argument name="magewire:mount:category-id" xsi:type="number">10</argument>
    </arguments>
</block>
```

Another page can bind `Vendor\Module\Magewire\ProductList` with a different
category ID. A theme can change the PHTML while keeping that PHP class.
An admin action or controller can call the same underlying Magento service
without copying business rules. See [Components](../essentials/components.md)
and [Best practices](../advanced/best-practices.md) for those patterns.

<a id="the-long-term"></a>

## Extend only what you need

Most modules need components, not new Magewire framework internals. A
[compatibility module](../theming/compatibility-module.md) contains
theme-specific loading and browser behavior; an ordinary Magento service
contains reusable business behavior. When a feature truly needs to
participate in Magewire's lifecycle, use a
[Feature](../advanced/architecture/features.md) or a
[Mechanism](../advanced/architecture/mechanisms/index.md).

Start with the [quickstart](../../index.md#quickstart) and add those layers
only when the feature calls for them.
