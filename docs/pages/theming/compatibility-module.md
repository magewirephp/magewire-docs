# Compatibility Module

A **compatibility module** is a standard Magento 2 module whose job is to adapt Magewire to one specific theme. This page walks through the minimum viable module and the decisions that take you from minimal to full-featured.

## Naming and location

Use the name `Vendor_MagewireCompatibilityWith{Theme}`. Place it in either:

- `app/code/Vendor/MagewireCompatibilityWith{Theme}/` for a project-local override, or
- A standalone composer package for reusable distribution.

Hyvä's own compatibility module lives in-tree under `magewirephp/magewire/themes/Hyva/` as an example of the second shape.

## Minimum viable module

Two files, nothing else:

```php title="registration.php"
<?php

\Magento\Framework\Component\ComponentRegistrar::register(
    \Magento\Framework\Component\ComponentRegistrar::MODULE,
    'Vendor_MagewireCompatibilityWithMyTheme',
    __DIR__
);
```

```xml title="etc/module.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Module/etc/module.xsd">
    <module name="Vendor_MagewireCompatibilityWithMyTheme">
        <sequence>
            <module name="Magewirephp_Magewire"/>
            <module name="Vendor_MyTheme"/>
        </sequence>
    </module>
</config>
```

The `sequence` block is load-bearing — it forces this module to load **after** both Magewire and your theme, so your DI and layout overrides win.

Enable it:

```
bin/magento module:enable Vendor_MagewireCompatibilityWithMyTheme
bin/magento setup:upgrade
```

At this point the module exists but does nothing. You add functionality by dropping files into it.

## Decision matrix

Pick only what you need. Each row below adds a capability.

| Want to… | Add |
|---|---|
| Override a core Magewire layout handle for the theme | `view/frontend/layout/default_{theme}.xml` |
| Override a Magewire PHTML template | `view/frontend/templates/…` (same path as in core) |
| Run a theme-scoped Feature / Component Hook | `etc/frontend/di.xml` + a class extending `\Magewirephp\Magewire\ComponentHook` |
| Register a Feature's PHTML into a layout container | `<referenceContainer name="magewire.features">` |
| Register a custom Alpine component | `<referenceContainer name="magewire.alpinejs.components">` |
| Register a custom `wire:*` directive | `<referenceContainer name="magewire.directives">` |
| Register a JavaScript utility / addon | `<referenceContainer name="magewire.utilities">` / `magewire.addons` |
| Bridge a Magento observer event | `etc/frontend/events.xml` + an observer class |
| Integrate with the theme's CSS build | An observer on the theme's build event |
| Provide theme-specific BC shims | A Feature + PHTML scripts in `magewire.internal.backwards-compatibility` |

See [Layout containers](layout-containers.md) for the full map.

## Area scoping

All Features, Hooks, and Mechanisms register via **area-scoped DI**:

- `etc/frontend/di.xml` — storefront
- `etc/adminhtml/di.xml` — admin
- **Never** `etc/di.xml` (global)

Global DI is ignored by the Magewire service provider. If registrations don't appear to take effect, this is almost always why.

## Example: flash-message bridge

Hyvä already dispatches its own flash messages via `dispatchMessages()`. Bridge Magewire's notifications to that function in three files.

**1. Register the Feature** — `etc/frontend/di.xml`:

```xml
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:ObjectManager/etc/config.xsd">
    <type name="Magewirephp\Magewire\MagewireServiceProvider">
        <arguments>
            <argument name="features" xsi:type="array">
                <item name="support_hyva_flash_messages" xsi:type="string">
                    Vendor\MagewireCompatibilityWithHyva\Magewire\Features\SupportHyvaFlashMessages
                </item>
            </argument>
        </arguments>
    </type>
</config>
```

(Exact argument name may vary by release — check the `MagewireServiceProvider` constructor.)

**2. Render the bridge script** — `view/frontend/layout/default_hyva.xml`:

```xml
<body>
    <referenceContainer name="magewire.features">
        <block name="magewire.features.support-hyva-flash-messages"
               template="Vendor_MagewireCompatibilityWithHyva::magewire-features/support-hyva-flash-messages.phtml" />
    </referenceContainer>
</body>
```

**3. The bridge script** — `view/frontend/templates/magewire-features/support-hyva-flash-messages.phtml`:

```html
<?php
$fragment = $block->getData('view_model')->utils()->template()->fragment();
$script = $fragment->script()->start();
?>
<script>
    window.addEventListener('magewire:flash-messages:dispatch', event => {
        dispatchMessages(event.detail);
    });
</script>
<?php $script->end(); ?>
```

Fragments handle CSP nonce/hash injection — never emit raw `<script>` tags.

## Anti-patterns

- Registering Features or Mechanisms in global `etc/di.xml`.
- Editing Magewire's base layout XML in place (patches break on upgrade).
- Emitting raw `<script>` / `<style>` tags instead of using [fragments](../concepts/fragments.md).
- Referencing theme-specific FQCNs from inside Magewire core — they belong in the compatibility module.
- Using `<referenceBlock>` where `<referenceContainer>` is the documented extension point — it replaces rather than adds.
- Shipping theme modules separately from the themes they compat with, without a `<sequence>` declaration.

## Related

- [Layout containers](layout-containers.md)
- [Alpine loading](alpine-loading.md)
- [Tailwind](tailwind.md)
- [Admin](../admin/index.md) — the canonical standalone compat module.
