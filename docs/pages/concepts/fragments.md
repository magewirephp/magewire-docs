# Fragments

!!! tip "Fragments can also be used outside Magewire components!"

Magewire includes a built-in implementation to support features such as Content Security Policy (CSP) compliance out of the box.
One key feature in this implementation is the use of Fragments and Fragment Modifiers.

Fragments are explicitly defined sections of code, marked by a developer using a `start()` and `end()` method.

## Defining a Fragment

Defining a fragment in your template is straightforward using the Magewire ViewModel's template utilities. In the example below,
we're creating a `script` fragment.

This fragment comes with a built-in CSP modifier. When rendered on a full-page cached page, a hash will be automatically
added to the dynamic CSP collection.

If the page is not cached, a nonce will be injected into the `<script>` tag instead.

```html
<?php

$magewireViewModel = $block->getData('view_model');
$fragment = $magewireViewModel->utils()->template()->fragment();
?>

<?php $script = $fragment->script()->start() ?>
<script>
    console.log('Custom Fragment');
</script>
<?php $script->end() ?>
```

!!! info "Fragment Modifiers"
    Each fragment type can have its own modifiers, which are injected via `di.xml`. You can inject custom logic by
    specifying a class that implements `Magewirephp\Magewire\Model\View\Fragment\Modifier`
    in the `modifiers` array of the constructor.

## Script Fragment

To better illustrate how typed fragments work, let's examine the script fragment implementation.
This fragment type requires validation, while any modifications are handled separately through modifiers.

A fragment must extend `Magewirephp\Magewire\Model\View\Fragment`. You can create a fragment using the `Magewirephp\Magewire\Model\View\FragmentFactory`
or via the Magewire ViewModel template utility with `$viewModel->utils()->template()->fragment()`.

```php title="Magewirephp\Magewire\Model\View\Fragment\Script"
<?php

class Script extends \Magewirephp\Magewire\Model\View\Fragment\Html
{
    public function start(): static
    {
        // ...
    }

    /**
     * Returns the content between the script tags.
     */
    public function getScriptCode(): string
    {
        // ...
    }
}
```

## Fragment Modifiers

Each fragment instance can have its own modifier, which is responsible for adjusting or enhancing the final output. Modifiers allow you to apply logic such as injecting a CSP hash, adding attributes, or manipulating content dynamically.

One important consideration when adding modifiers is the sort order. Modifiers are applied in sequence, so the order in which they are executed can significantly affect the final result.

To inject custom modifiers into a fragment, use Magento’s `di.xml` configuration.

Here’s a basic outline:

```xml
<type name="Magewirephp\Magewire\Model\View\Fragment\Script">
    <arguments>
        <argument name="modifiers" xsi:type="array">
            <!-- Maximum sort order to make sure this modifier is run last. -->
            <item name="csp" sortOrder="9999" xsi:type="object">
                Magewirephp\Magewire\Model\View\Fragment\Modifier\Csp
            </item>
        </argument>
    </arguments>
</type>
```

A modifier has access to the raw fragment code. The CSP modifier either includes a hash of the inline JavaScript within
the `<script>` tags or adds a `nonce="..."` attribute to the script tag when the page is not cached.

```php title="Magewirephp\Magewire\Model\View\Fragment\Modifier\Csp"
<?php

class Csp extends \Magewirephp\Magewire\Model\View\Fragment\Modifier
{
    public function modify(string $output, Fragment $fragment): string
    {
        if (! $fragment instanceof Fragment\Script) {
            return $output;
        }
    
        // ...
    
        return $output;
    }
}
```
