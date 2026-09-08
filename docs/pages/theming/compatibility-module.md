# Compatibility Module

A **compatibility module** is a standard Magento 2 module whose job is to adapt Magewire to one specific theme. This page walks through the minimum viable module and the decisions that take you from minimal to full-featured.

## Naming and location

Use the name `Vendor_MagewireCompatibilityWith{Theme}`. Place it in either:

- `app/code/Vendor/MagewireCompatibilityWith{Theme}/` for a project-local override, or
- A standalone composer package for reusable distribution.

Hyvä's own compatibility module is the standalone `magewirephp/magewire-hyva-theme` package, an example of the
second shape. Before 3.2.0 it lived in-tree under the core repository's `themes/Hyva/` directory. The directory was
removed when maintained integrations moved into separate packages, although core 3.6 still contains a legacy Hyvä
build-config observer.

<a id="minimum-viable-module"></a>

## Minimum viable project-local module

An `app/code` module needs these two files:

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

The `sequence` block is load-bearing because it forces this module to load **after** both Magewire and your theme, so your DI and layout overrides win.

Enable it:

```
bin/magento module:enable Vendor_MagewireCompatibilityWithMyTheme
bin/magento setup:upgrade
```

At this point the module exists but does nothing. You add functionality by dropping files into it.

A reusable Composer package also needs a `composer.json` that declares `"type": "magento2-module"`, loads
`registration.php` through `autoload.files`, and maps the module namespace through `autoload.psr-4`.

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

Register Magewire's `Features` and `Mechanisms` item collections in the area where they run:

- `etc/frontend/di.xml`: storefront
- `etc/adminhtml/di.xml`: admin
- `etc/di.xml`: valid for preferences, plugins, and normal constructor configuration that is genuinely global

Magewire's collection arrays are configured at Magento's area-specific DI stage. An item added to the same array in
global `etc/di.xml` can be replaced when Magento loads the later area configuration. Follow the scope of the
collection being extended.

<a id="example-flash-message-bridge"></a>

## Reuse maintained theme behavior

Before adding a bridge, inspect the maintained compatibility package. For example,
`magewirephp/magewire-hyva-theme` already bridges Magewire flash messages to Hyvä's
`dispatchMessages()`. Reimplementing that bridge in a project module duplicates behavior and can drift from the
package.

Use a project compatibility module only for behavior specific to your theme or store. Register its browser output in
the appropriate [layout container](layout-containers.md), and wrap inline scripts in a
[Script fragment](../concepts/fragments.md) for CSP handling.

## Anti-patterns

- Registering Feature or Mechanism item collections in global `etc/di.xml`.
- Editing Magewire's base layout XML in place (patches break on upgrade).
- Emitting raw `<script>` / `<style>` tags instead of using [fragments](../concepts/fragments.md).
- Referencing theme-specific FQCNs from inside Magewire core: they belong in the compatibility module.
- Assuming `referenceBlock` replaces a block or `referenceContainer` is inherently additive. Both reference an existing layout node; child addition and template/argument changes determine the result. Follow the node and pattern used by the current first-party package.
- Shipping theme modules separately from the themes they compat with, without a `<sequence>` declaration.

## Related

- [Layout containers](layout-containers.md)
- [Alpine loading](alpine-loading.md)
- [Tailwind](tailwind.md)
- [Admin](../admin/index.md): the canonical standalone compat module.
