<a id="compatibility-module"></a>

# Build a compatibility module

A compatibility module keeps theme-specific code out of your reusable
components. Your PHP class can serve several storefronts; a small companion
module provides the layout, Alpine, CSS, or template changes needed by one
theme.

<a id="example-flash-message-bridge"></a>

Install an existing integration first. For Hyvä, use
[`magewirephp/magewire-hyva-theme`](https://github.com/magewirephp/magewire-hyva-theme).
It already coordinates the Alpine loader and bridges Magento flash messages.
The example below adds one reusable Hyvä behavior on top of that package.

<a id="naming-and-location"></a>
<a id="minimum-viable-module"></a>

## Package the integration

Create a Composer package with this structure:

```text
vendor/module-magewire-hyva-extras/
├── composer.json
└── src/
    ├── registration.php
    ├── etc/module.xml
    └── view/frontend/
        ├── layout/default_hyva.xml
        └── templates/js/magewire-disclosure.phtml
```

The dependencies make the package installable in any project that uses
Magewire 3 and the maintained Hyvä integration:

```json title="composer.json"
{
  "name": "vendor/module-magewire-hyva-extras",
  "description": "Reusable Magewire UI behavior for Hyvä",
  "type": "magento2-module",
  "require": {
    "magewirephp/magewire": "^3.6",
    "magewirephp/magewire-hyva-theme": "^3.1"
  },
  "autoload": {
    "files": ["src/registration.php"]
  }
}
```

Register the Magento module and sequence it after the package whose layout
nodes you extend:

```php title="src/registration.php"
<?php

use Magento\Framework\Component\ComponentRegistrar;

ComponentRegistrar::register(
    ComponentRegistrar::MODULE,
    'Vendor_MagewireHyvaExtras',
    __DIR__
);
```

```xml title="src/etc/module.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Module/etc/module.xsd">
    <module name="Vendor_MagewireHyvaExtras">
        <sequence>
            <module name="Magewirephp_Magewire"/>
            <module name="Magewirephp_MagewireHyvaTheme"/>
            <module name="Hyva_Theme"/>
        </sequence>
    </module>
</config>
```

For a project-local module in `app/code`, use the same `registration.php` and
`etc/module.xml` layout. Composer metadata matters when you distribute it.

If the package restyles Magewire's own UI, require `magewirephp/magewire` `^3.7`
(and `magewirephp/magewire-hyva-theme` `^3.1.2` on Hyvä). Magewire 3.7.0 replaced
the notifier, loading icon, and exception markup with the classes documented in
[Core styles](styles.md).

## Register shared browser behavior

The Hyvä integration uses the `default_hyva` layout handle. Add a block to
Magewire's Alpine component container; the block inherits the Magewire view
model from the root layout block:

```xml title="src/view/frontend/layout/default_hyva.xml"
<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <body>
        <referenceContainer name="magewire.alpinejs.components">
            <block name="vendor.magewire.hyva.disclosure"
                   template="Vendor_MagewireHyvaExtras::js/magewire-disclosure.phtml"/>
        </referenceContainer>
    </body>
</page>
```

Wrap inline JavaScript in a Script fragment so Magewire can supply the CSP
nonce or hash. This follows the pattern used by the maintained Hyvä package:

```php title="src/view/frontend/templates/js/magewire-disclosure.phtml"
<?php

/** @var \Magento\Framework\View\Element\Template $block */
$magewireViewModel = $block->getData('view_model');
$fragment = $magewireViewModel->utils()->fragment();
?>
<?php $script = $fragment->make()->script()->start() ?>
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('magewireDisclosure', () => ({
            open: false,
            toggle() { this.open = ! this.open }
        }));
    }, { once: true });
</script>
<?php $script->end() ?>
```

Any component template in the project can now use the same browser behavior:

```php title="view/frontend/templates/magewire/counter.phtml"
<div x-data="magewireDisclosure">
    <button type="button" x-on:click="toggle" x-bind:aria-expanded="open">
        <?= $escaper->escapeHtml(__('Show counter')) ?>
    </button>

    <div x-show="open" x-cloak>
        <span><?= $escaper->escapeHtml(__('Count: %1', $magewire->count)) ?></span>
        <button type="button" wire:click="increment">
            <?= $escaper->escapeHtml(__('Increase')) ?>
        </button>
    </div>
</div>
```

The disclosure state stays in Alpine; the count stays in the Magewire
component. That division lets several PHP components use the same browser
behavior without copying scripts into every PHTML file.

Install the package with Composer, enable `Vendor_MagewireHyvaExtras` if needed,
run `bin/magento setup:upgrade`, and rebuild the Hyvä frontend assets if the
package also contributes Tailwind sources.

## Adapt another theme

For a theme without a maintained Magewire package, start with the same Magento
module structure. Use a layout handle that your theme actually adds; the
`default_hyva` handle above belongs to Hyvä and is not a Magento convention
for every theme. A general `default.xml` applies wherever the module is enabled,
which matters in stores with more than one active theme.

The first integration decision is script ownership. Magewire bundles Alpine.
Your module must place the Magewire loader at the right layout node and
coordinate the theme's own Alpine asset so one instance starts on a page.
The [Hyvä loader layout](https://github.com/magewirephp/magewire-hyva-theme/blob/main/src/view/frontend/layout/default_hyva.xml)
and [script template](https://github.com/magewirephp/magewire-hyva-theme/blob/main/src/view/frontend/templates/script.phtml)
are concrete references. Then add only the CSS and browser bridges your theme
needs. Since Magewire 3.7, core ships complete styles for its own UI, so a new
integration can adjust the [core style tokens](styles.md) instead of supplying
notifier or loading-indicator CSS. Keep PHP business services in the feature
module; put theme behavior in this companion module.

<a id="decision-matrix"></a>

## Extend and replace layout output

Add a child to an existing container when you want additional output:

```xml
<referenceContainer name="magewire.features">
    <block name="vendor.magewire.theme-bridge"
           template="Vendor_MagewireHyvaExtras::js/theme-bridge.phtml"/>
</referenceContainer>
```

Change an existing block's template when you need a replacement:

```xml
<referenceBlock name="magewire.ui-components.notifier"
                template="Vendor_MagewireHyvaExtras::magewire/notifier.phtml"/>
```

The replacement template must provide the behavior expected by that block. For
the notifier, keep the classes and attributes listed under
[Notifier markup](styles.md#notifier-markup) so the core styles and theme tokens
still apply. Merely placing a PHTML file at the same relative path in your
module does not replace another module's template. Prefer adding a child or a small feature
bridge when it meets the need; replacing a whole core template ties your
package to its internal markup.

<a id="area-scoping"></a>

If your integration registers a Magewire Feature or Mechanism, add its
collection item in `etc/frontend/di.xml`. For admin extensions use
`etc/adminhtml/di.xml`. Magento's area configuration can replace collection
arrays declared in global `etc/di.xml`.

<a id="anti-patterns"></a>
<a id="related"></a>

## Check both page types

Test one page with a Magewire component and one page without one. Confirm the
component updates, Alpine initializes once, CSP permits your script, and the
theme still works when Magewire does not drive the page. Test again with
Magento full-page cache enabled. To check style overrides, open the
[UI workbench](styles.md#preview-with-the-ui-workbench) at
`/magewire/playwright/ui`, which renders the real notifier, loading icon, and
exception markup. See [Alpine loading](alpine-loading.md),
[Layout nodes](layout-containers.md), [Core styles](styles.md), and
[Tailwind](tailwind.md) for each integration point.
