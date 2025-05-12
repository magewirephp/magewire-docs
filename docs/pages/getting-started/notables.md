# Notables

Notables are brief, helpful insights that highlight useful context or nuances. They’re not meant to be buried in the main text,
nor do they require a full deep-dive explanation — they simply make small but important details clearer at a glance.

## The Magewire Block

We aim to keep JavaScript-related .phtml files as minimal and clean as possible. These templates are architected to live
within a wrapping `magewire` block, which comes with both benefits and trade-offs. One such trade-off is that many of
these blocks require the `Magewirephp\Magewire\ViewModel\Magewire` view model to function properly.

Manually assigning a `view_model` argument to each block would not only be tedious but would also result in a significant
increase in XML configuration lines. To address this, Magewire includes a small feature that automatically injects the
`view_model` argument into all sibling blocks contained within a `magewire` block.

In practice, this means that as long as your block resides inside the `magewire` block—whether directly or as a
sibling—you can access the view model via `$block->getViewModel()` or `$block->getData('view_model')`.

```xml
<!-- A container that sits within the "magewire" block. -->
<referenceContainer name="magewire.features">
    
    <!-- The "view_model" argument is automatically bound. -->
    <block name="foo" template="..."/>
</referenceContainer>
```

However, please note: if you move a block outside the `magewire` wrapper block, you'll need to manually bind the
`view_model` argument. This is precisely why the view model is passed as an argument instead of being exposed as
a global dictionary variable—to avoid forcing developers to rewrite the template just to maintain compatibility.

Also, if the block already has a `view_model` argument defined, Magewire will skip it automatically.

## Magewire View Model

!!! info "Subject Class: \Magewirephp\Magewire\ViewModel\Magewire"

In Magewire V1, the Magewire View Model gradually became a collection of helper methods, mostly used to pass small bits
of data to templates. This approach was functional, but over time, it became cluttered. In Magewire V3, this has been overhauled:
many of those helper methods have been deprecated and moved into dedicated utility classes, accessible via the `utils()` method.

```html title="view/frontend/templates/example.phtml"
<?php

$magewireViewModel = $block->getData('view_model')

<?php if ($magewireViewModel->utils()->env()->isDeveloperMode()): ?>
    ...
<?php endif ?>
```

You can extend this system by implementing the `Magewirephp\Magewire\Model\View\UtilsInterface` in your own utility class:

```xml title="etc/di.xml"
<type name="Magewirephp\Magewire\Model\View\Utils">
    <arguments>
        <argument name="utilities" xsi:type="array">
            <item name="myCustomTechnology" xsi:type="object">
                Example\Module\Magewire\Features\SupportCustomTechnology\View\Utils\MyCustomTechnology
            </item>
        </argument>
    </arguments>
</type>
```

Your utility class might look like this:

```php title="Example/Module/Magewire/Featuers/SupportCustomTechnology/View/Utils/MyCustomTechnology.php"
<?php

namespace Example\Module\Magewire\Features\SupportCustomTechnology\View\Utils;

class MyCustomTechnology implements \Magewirephp\Magewire\Model\View\UtilsInterface
{
    public function foo(): string {}
    public function bar(): string {}
}
```

To finally have:

```html title="view/frontend/templates/example.phtml"
<?php

$magewireViewModel = $block->getData('view_model')

// Two examples on how to call your custom utility.
$foo = $magewireViewModel->utils('myCustomTechnology')->foo();
$bar = $magewireViewModel->utils()->myCustomTechnology()->bar();
```

*Note: Providing a custom View Model directly is still perfectly valid.*
