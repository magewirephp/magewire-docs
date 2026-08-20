# Layout Nodes

Magewire renders its browser resources through a named Magento layout tree. Compatibility modules extend that tree instead of copying core layout XML.

## Core reference

| Name | Kind | Purpose |
|---|---|---|
| `magewire` | block | Root of Magewire's rendered resources. |
| `magewire.global` | block | Creates the addon and utility registries. |
| `magewire.alpinejs.load` | container | Theme package injection point for the selected Alpine/Magewire loader. |
| `magewire.alpinejs` | container | Alpine registrations that run before reusable components. |
| `magewire.alpinejs.components` | container | `Alpine.data()` component registrations. |
| `magewire.utilities` | block | Built-in `MagewireUtilities` registrations. Add late utilities under `magewire.utilities.after`. |
| `magewire.addons` | block | Built-in `MagewireAddons` registrations. Add late addons under `magewire.addons.after`. |
| `magewire.before` | container | Theme-facing content before Magewire internals. |
| `magewire.ui-components` | container | Rendered Alpine UI, including the notifier. |
| `magewire.internal` | block | Internal bridge output; do not override casually. |
| `magewire.internal.backwards-compatibility` | container | V1 browser compatibility shims. |
| `magewire.directives` | block | Custom Magewire directive registrations. |
| `magewire.features` | block | Browser bridges for PHP features, including loaders, request filters, and lazy loading. |
| `magewire.after.internal` | container | Safe injection point immediately after internals. |
| `magewire.after` | container | General late content. |
| `magewire.disabled` | container | Output used only when Magewire is disabled. |
| `magewire.legacy` | container | V1 compatibility tree; not rendered unless a theme moves it. |

`magewire.script` is not a core storefront block. The current admin companion package defines that name inside its own `magewire.head` block; do not target it from a storefront integration.

## Referencing nodes

`referenceBlock` and `referenceContainer` both modify an existing layout node; neither replaces content merely by being referenced. Use the reference type expected by the layout structure and the current first-party integration pattern. Replacement happens when you change a target's template or arguments, while declaring a child adds to its output.

First-party theme packages commonly add feature children like this:

```xml
<referenceContainer name="magewire.features">
    <block name="vendor.magewire.features.my-bridge"
           template="Vendor_Module::magewire-features/my-bridge.phtml" />
</referenceContainer>
```

For the registries, prefer their dedicated late containers so core registrations remain first:

```xml
<referenceContainer name="magewire.utilities.after">
    <block name="vendor.magewire.utilities.currency"
           template="Vendor_Module::js/magewire/utilities/currency.phtml" />
</referenceContainer>
```

## Ordering

Magento's normal `before` and `after` attributes control siblings:

```xml
<referenceContainer name="magewire.alpinejs.components">
    <block name="vendor.search"
           template="Vendor_Module::js/alpinejs/search.phtml"
           after="magewire.alpinejs.components.magewire-notifier" />
</referenceContainer>
```

Choose an ordering dependency that is guaranteed by a sequenced module. Avoid copying the complete Magewire layout tree into a theme because that prevents new core resources from appearing after upgrades.

All inline scripts should use a [fragment](../concepts/fragments.md) so Magento CSP metadata can be applied.
