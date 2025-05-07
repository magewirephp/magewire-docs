### 1. Create a Component class

Create a new component class:

```php title="File: Magewire/Counter.php"
<?php

namespace Vendor\Module\Magewire;

class Counter extends \Magewirephp\Magewire\Component
{
    public int $count = 0;

    public function increment(): void
    {
        $this->count++;
    }
}
```

**Note:** It is advisable to keep your components inside the `Magewire` root directory of your module,
either as direct children or nested within subdirectories.

### 2. Create a Template File

Now, create the corresponding template file:

```html title="File: view/frontend/templates/magewire/counter.phtml"
<div>
    Counter: <?= $magewire->count ?>
    
    <button wire:click="increment">
        Increase
    </button>
</div>
```

**Note:** Every Magewire component binds its state to the first HTML element in its template.
This means you must always wrap your component's content in a root HTML element,
such as a `<div>`, to ensure proper functionality.

### 3. Inject onto a page

To render the component, add the following to your layout handle:

```xml title="File: view/frontend/layout/page_handle.xml"
<referenceBlock name="content">
    <block name="counter.block" template="Vendor_Module::magewire/counter.phtml">
        <arguments>
            <argument name="magewire" xsi:type="object">
                Vendor\Module\Magewire\Counter
            </argument>
        </arguments>
    </block>
</referenceBlock>
```

**Note:** This is the standard method for injecting a Magewire component into your page.
However, alternatives exist through component resolvers, allowing more flexible integration.
You can even create a custom resolver to fit specific requirements.

### 4. Test it out

<img src="./images/counter.gif" alt="Counter" style="border-radius: 15px">

Clear the Magento cache and navigate to the relevant page:

```sh
bin/magento cache:flush
```
