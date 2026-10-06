# Events

Events let one Magewire component tell another that something changed. The
sender does not need to know which other component is listening, which keeps
both components reusable.

## Dispatch an event

Here a category picker publishes the selected ID. The action validates the
browser-supplied value before dispatching it:

```php title="Magewire/CategoryPicker.php"
<?php

namespace Vendor\Module\Magewire;

use Magento\Framework\Exception\LocalizedException;
use Magewirephp\Magewire\Component;

class CategoryPicker extends Component
{
    public function select(int $categoryId): void
    {
        if ($categoryId < 1) {
            throw new LocalizedException(__('Choose a category.'));
        }

        $this->dispatch('category-selected', categoryId: $categoryId);
    }
}
```

```php title="view/frontend/templates/magewire/category-picker.phtml"
<div>
    <button type="button" wire:click="select(10)">
        <?= $escaper->escapeHtml(__('Show category 10')) ?>
    </button>
</div>
```

## Listen in another component

`#[On]` registers a method as a listener. The named event argument becomes
the method argument:

```php title="Magewire/CategorySummary.php"
<?php

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Attributes\On;
use Magewirephp\Magewire\Component;

class CategorySummary extends Component
{
    public int $categoryId = 0;

    #[On('category-selected')]
    public function showCategory(int $categoryId): void
    {
        $this->categoryId = $categoryId;
    }
}
```

```php title="view/frontend/templates/magewire/category-summary.phtml"
<div>
    <?php if ($magewire->categoryId > 0): ?>
        <?= $escaper->escapeHtml(__('Selected category: %1', $magewire->categoryId)) ?>
    <?php else: ?>
        <?= $escaper->escapeHtml(__('Choose a category above.')) ?>
    <?php endif ?>
</div>
```

Bind each class to its own layout block using the
[component layout pattern](components.md#create-your-first-component).
The listener can now appear elsewhere on the page without changing the picker.
Use descriptive event names if several integrations share a page.

<a id="listener-targets"></a>

## Choose a listener method

A listener must point at a public method you define on the component. Since Magewire 3.7.2, a listener that points at
a method inherited from `Component` or `Component\Form`, such as `reset`, or at a lifecycle hook, such as `mount`,
throws `MethodNotFoundException` when the event arrives. Wrap the helper in a method of your own:

```php
#[On('filters-cleared')]
public function clearFilters(): void
{
    $this->reset('categoryId');
}
```

The rule covers `#[On]`, the `$listeners` property, and
[layout overrides](../features/layout-overrides.md#listeners).

## Browser listeners

Component events are browser events too. A theme integration can listen for
one when it needs to update browser-only UI:

```javascript
window.addEventListener('category-selected', event => {
    console.log(event.detail.categoryId)
})
```

Put production listeners in a [compatibility module](../theming/compatibility-module.md)
and wrap inline scripts in a [Script fragment](../concepts/fragments.md#the-script-fragment).
The old `emit*()` helpers are V1 migration APIs; new components use
`dispatch()`, and `#[On]` rather than the `$listeners` property.

## Per-placement listeners

Since Magewire 3.7, a layout block can add, reassign, or remove listeners for
one placement of a component without changing its class:

```xml
<argument name="magewire:listeners" xsi:type="array">
    <item name="category-selected" xsi:type="string">onCategorySelected</item>
    <item name="category-cleared" xsi:type="null"/>
</argument>
```

See [Layout overrides](../features/layout-overrides.md#listeners) for
precedence, placeholders, and what happens when a removed event is still
dispatched.

<a id="framework-hooks-are-different"></a>
<a id="magento-observers"></a>

Magewire's internal `on()` and `trigger()` hooks serve framework extensions
and are separate from these component events. See
[Component hooks](../advanced/architecture/component-hooks.md) and
[Magento observer events](../advanced/architecture/observer-events.md).
