### 1. Create the component class

Create the component below inside your Magento module:

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

Public properties hold the component state. Public methods can be called from the template, so treat their arguments as
untrusted input and perform the same validation and authorization you would use in a controller.

### 2. Create the template

The corresponding template reads state through the injected `$magewire` variable:

```php title="view/frontend/templates/magewire/counter.phtml"
<div>
    <span>
        <?= $escaper->escapeHtml(__('Counter: %1', $magewire->count)) ?>
    </span>

    <button type="button" wire:click="increment">
        <?= $escaper->escapeHtml(__('Increase')) ?>
    </button>
</div>
```

Every component template must have one root HTML element. Magewire attaches the component snapshot to that element and
morphs its contents after an update.

### 3. Bind it in layout XML

Add a block to the layout handle where the component should appear:

```xml title="view/frontend/layout/page_handle.xml"
<referenceContainer name="content">
    <block name="vendor.module.counter"
           template="Vendor_Module::magewire/counter.phtml">
        <arguments>
            <argument name="magewire" xsi:type="object">
                Vendor\Module\Magewire\Counter
            </argument>
        </arguments>
    </block>
</referenceContainer>
```

The built-in layout resolver turns the block's `magewire` argument into the component instance. Custom resolvers are
available for integrations that cannot use this standard block-and-argument shape.

### 4. Clear layout caches and try it

```shell
bin/magento cache:clean layout full_page
```

Open the page represented by the layout handle. Clicking **Increase** sends a Magewire update request, calls
`increment()`, renders the template again, and morphs the changed counter into the existing DOM.
