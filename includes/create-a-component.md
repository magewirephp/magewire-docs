<a id="1-create-the-component-class"></a>

### 1. Add a component to your Magento module

This example adds a counter to the CMS home page. Start in an existing, enabled
`Vendor_Module` module. The three files are:

```text
Vendor/Module/
├── Magewire/Counter.php
└── view/frontend/
    ├── layout/cms_index_index.xml
    └── templates/magewire/counter.phtml
```

```php title="Magewire/Counter.php"
<?php

declare(strict_types=1);

namespace Vendor\Module\Magewire;

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

The public property is browser-visible state. The public method is an action the
browser can call; validate and authorize actions that read or change business data.

<a id="2-create-the-template"></a>

### 2. Render it with PHTML

Magewire makes the component available to its template as `$magewire`:

```php title="view/frontend/templates/magewire/counter.phtml"
<div data-testid="magewire-counter">
    <span><?= $escaper->escapeHtml(__('Count: %1', $magewire->count)) ?></span>

    <button type="button" wire:click="increment">
        <?= $escaper->escapeHtml(__('Increase')) ?>
    </button>
</div>
```

Keep one root element. Magewire uses it to attach the component snapshot and to
update the rendered HTML. Escape text and attributes using Magento's `$escaper`.

<a id="3-bind-it-in-layout-xml"></a>

### 3. Place it with layout XML

The `cms_index_index` handle places the counter on the CMS home page:

```xml title="view/frontend/layout/cms_index_index.xml"
<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <body>
        <referenceContainer name="content">
            <block name="vendor.module.counter"
                   template="Vendor_Module::magewire/counter.phtml">
                <arguments>
                    <argument name="magewire" xsi:type="object" shared="false">
                        Vendor\Module\Magewire\Counter
                    </argument>
                </arguments>
            </block>
        </referenceContainer>
    </body>
</page>
```

The `magewire` argument binds the PHP class to this block. `shared="false"` gives
the block its own component instance, which also makes the pattern safe when you
place the same class more than once on a page.

<a id="4-clear-layout-caches-and-try-it"></a>

### 4. Try it

```shell
bin/magento cache:clean layout block_html full_page
```

Open the home page and click **Increase**. Magewire calls `increment()` on the
server and updates the count without a full page reload. If the block does not
appear, confirm the module is enabled and that this page uses `cms_index_index`.
