# Breeze storefront

If your store uses [Breeze](https://breezefront.com/docs), you do not need to
write the Magewire runtime bridge from scratch. The
[`swissup/module-breeze-magewire`](https://github.com/breezefront/module-breeze-magewire)
package provides the Breeze layout and browser integration for Magewire V3.
Your component classes and actions remain ordinary Magewire code.

## Install the integration

Start with an enabled Breeze storefront. From the Magento project root,
install Magewire V3 and the companion package:

```shell
composer require 'magewirephp/magewire:^3' swissup/module-breeze-magewire
bin/magento module:enable Magewirephp_Magewire Swissup_BreezeMagewire
bin/magento setup:upgrade
bin/magento cache:clean layout block_html full_page
```

The integration package's current
[`composer.json`](https://github.com/breezefront/module-breeze-magewire/blob/master/composer.json)
does not declare Magewire
or Breeze as Composer dependencies. Install and enable both explicitly;
installing this module alone does not set up either runtime. If
you still need Breeze itself, follow its
[installation and activation instructions](https://github.com/breezefront/module-breeze#installation).

You can check the Magento module state before testing the browser:

```shell
bin/magento module:status Magewirephp_Magewire Swissup_Breeze Swissup_BreezeMagewire
```

## What the package connects

The package contributes
[`view/frontend/layout/breeze_default.xml`](https://github.com/breezefront/module-breeze-magewire/blob/master/view/frontend/layout/breeze_default.xml), so its
blocks run when Breeze applies that layout handle. It places the Magewire
script and a small Alpine runtime host inside `magewire.alpinejs.load`. The
host transfers Magewire's update URL and CSRF data to the script element.
These blocks are conditional on a page having Magewire components, as in the
Magewire core. The package also adds a flash-message listener that updates
Magento customer-data through Breeze's `require` shim. It preserves Breeze's
`scroll-reveal` class while Magewire morphs the DOM.

Those are theme concerns. You can keep the same PHP component, service, and
actions when you use a second storefront theme:

```php title="Model/Magewire/Counter.php"
<?php

declare(strict_types=1);

namespace Vendor\Counter\Model\Magewire;

use Magewirephp\Magewire\Component;

class Counter extends Component
{
    public int $count = 0;

    public function increment(): void
    {
        $this->count++;
    }
}
```

```php title="view/frontend/templates/magewire/counter.phtml"
<div>
    <span><?= $escaper->escapeHtml(__('Count: %1', $magewire->count)) ?></span>
    <button type="button" wire:click="increment">
        <?= $escaper->escapeHtml(__('Increase')) ?>
    </button>
</div>
```

Bind it in your feature module's normal Magento layout. The Breeze package
handles the runtime; the feature module owns the component:

```xml title="view/frontend/layout/cms_index_index.xml"
<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <body>
        <referenceContainer name="content">
            <block name="vendor.counter"
                   template="Vendor_Counter::magewire/counter.phtml">
                <arguments>
                    <argument name="magewire" xsi:type="object" shared="false">
                        Vendor\Counter\Model\Magewire\Counter
                    </argument>
                </arguments>
            </block>
        </referenceContainer>
    </body>
</page>
```

For the full first-component walkthrough, see the
[quickstart](../../index.md#quickstart).

## Add Breeze-only behavior

Put any styling or browser bridge that exists *only* for Breeze in a small
companion module. Use `breeze_default.xml` so it does not affect another
storefront theme. This example adds a hook for a class applied by Breeze-side
JavaScript; the PHP component stays unchanged:

```xml title="view/frontend/layout/breeze_default.xml"
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <body>
        <referenceBlock name="magewire.features">
            <block name="vendor.counter.breeze-classes"
                   template="Vendor_CounterBreeze::js/preserve-classes.phtml"/>
        </referenceBlock>
    </body>
</page>
```

```php title="view/frontend/templates/js/preserve-classes.phtml"
<?php
$fragment = $block->getData('view_model')->utils()->fragment();
?>
<?php $script = $fragment->make()->script()->start() ?>
<script>
    document.addEventListener('livewire:init', () => {
        Magewire.hook('morph', ({ el, toEl }) => {
            if (el.hasAttribute('data-breeze-keep-open') && el.classList.contains('is-open')) {
                toEl.classList.add('is-open');
            }
        });
    }, { once: true });
</script>
<?php $script->end() ?>
```

Apply `data-breeze-keep-open` only to markup whose `is-open` class is managed
outside Magewire. Prefer a Magewire property or Alpine state for interactive
state you own; a morph hook is for integrating with another script. The Script
fragment lets Magewire handle the inline script's CSP requirements. For a
distributable companion module, use the
[compatibility-module guide](compatibility-module.md) for Composer packaging,
registration, and module sequencing.

## Verify both page types

Open the example page and click **Increase**. The count should update without
a navigation. Inspect the rendered HTML: a Magewire component page should
have one `#magewire-script`, with `data-update-uri` and `data-csrf` on it.
Check a page without components as well; it should retain normal Breeze
behavior without an extra Magewire runtime. If the component renders but does
not update, first check that Breeze is active for that store view and that the
`breeze_default` layout handle is present. Then inspect the browser console,
network request, and [Alpine loading](alpine-loading.md) guidance.
