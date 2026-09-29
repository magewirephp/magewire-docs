# Layout Overrides

{{ include("admonition/magewire-specific.md", since_version="3.7.0") }}

A component class can be placed in several layout blocks. Three block arguments adjust one placement without
subclassing the component or changing its `$listeners` and `$loader` properties:

| Argument | Adjusts |
|---|---|
| `magewire:listeners` | Which events the component listens to, and which method handles each one. |
| `magewire:loader` | The [loader messages](../advanced/javascript/features/magewire-loaders.md) shown during requests. |
| `magewire:modifiers` | Anything else, through PHP objects that run while the component is built. |

```xml title="view/frontend/layout/checkout_cart_index.xml"
<referenceBlock name="vendor.cart.summary">
    <arguments>
        <argument name="magewire:listeners" xsi:type="array">
            <!-- Add a listener. -->
            <item name="shipping-method-changed" xsi:type="string">refresh</item>
            <!-- Give an existing listener another handler. -->
            <item name="cart-updated" xsi:type="string">refreshTotals</item>
            <!-- Remove a listener declared by the class, #[On], or an earlier layout file. -->
            <item name="coupon-applied" xsi:type="null"/>
        </argument>
        <argument name="magewire:loader" xsi:type="array">
            <item name="refresh" xsi:type="string">Updating totals ... Totals updated</item>
            <item name="applyCoupon" xsi:type="null"/>
        </argument>
        <argument name="magewire:modifiers" xsi:type="array">
            <item name="store_scope" xsi:type="object" shared="false">Vendor\Module\Magewire\Modifier\StoreScope</item>
        </argument>
    </arguments>
</referenceBlock>
```

Magento merges array arguments across layout files by item name, so a later layout file can change or remove an
item that an earlier one added.

## Listeners

Each item in `magewire:listeners` is keyed by an event name:

| Item value | Effect |
|---|---|
| `xsi:type="string"` with a method name | Adds the listener, or replaces the handler of an existing one. |
| `xsi:type="null"` or `xsi:type="boolean">false` | Removes the listener. |

The listener map is built in this order, where a later source wins for the same event name:

1. the component's `$listeners` property;
2. `#[On]` attributes;
3. `magewire:listeners`, merged across layout files;
4. [modifiers](#modifiers) that change the `listeners` argument.

A removed listener is left out of the event names the browser subscribes to on the first render. If a dispatch for
that name still reaches the server, the request fails with `EventHandlerDoesNotExist`
(`Handler for event … does not exist`). Before 3.7.0, the exception class itself was missing, so dispatching an event
without a handler failed with a class-not-found error instead.

Event names can contain `{property}` placeholders, such as `cart-updated:{storeId}`. They are resolved against the
component's state for listeners you add and for listeners you remove.

!!! note "Shorthand listeners can be removed, not reassigned"
    A class listener declared without a key, such as `protected $listeners = ['refresh'];`, can be removed from layout.
    Giving it another handler from layout has no effect, because the shorthand entry is matched first. Declare the
    listener with an explicit event name in the class if placements need different handlers.

Magewire does not check that a handler method exists when the block is built. A missing method fails when the
event arrives.

## Loader messages

`magewire:loader` is merged over the class `$loader` map for this block only:

| Item value | Effect |
|---|---|
| `xsi:type="string"` | Sets or replaces the messages for that key. The string is translated with `__()`. |
| `xsi:type="null"` | Removes the key, so a broader key such as `*` can match instead. |
| `xsi:type="boolean">false` | Keeps the key with a `false` value. The action matches it and shows no notification, and broader keys are not used. |

`<argument name="magewire:loader" xsi:type="null"/>` turns off loader messages for the whole block. Use a keyed map
otherwise; a single string for the whole argument is accepted by the server but not displayed by the current
browser code.

The component's own `getLoader()` keeps returning the class value. See
[Magewire Loaders](../advanced/javascript/features/magewire-loaders.md) for keys and message syntax.

## Modifiers

A modifier is a PHP class that implements
`Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentModifiers\ModifierInterface`:

```php title="Magewire/Modifier/StoreScope.php"
<?php

declare(strict_types=1);

namespace Vendor\Module\Magewire\Modifier;

use Magento\Store\Model\StoreManagerInterface;
use Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentModifiers\ComponentModifierContext;
use Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentModifiers\ModifierInterface;
use Vendor\Module\Magewire\CartSummary;

class StoreScope implements ModifierInterface
{
    public function __construct(
        private readonly StoreManagerInterface $storeManager
    ) {
    }

    public function modify(ComponentModifierContext $context): void
    {
        if (! $context->component() instanceof CartSummary) {
            return;
        }

        $storeCode = $this->storeManager->getStore()->getCode();
        $arguments = $context->arguments();

        $listeners = $arguments->get('listeners', []);
        $listeners['cart-updated:' . $storeCode] = 'refresh';

        $loader = $arguments->get('loader', []);
        $loader['refresh'] = [__('Refreshing cart')];

        $arguments->merge(['listeners' => $listeners, 'loader' => $loader]);
    }
}
```

`ComponentModifierContext` gives access to the component through `component()` and to the block's
`MagewireArguments` through `arguments()`.

- **Timing.** Modifiers run while the component is built, on the first render and on every update request. They run
  after the block's arguments are collected and before the component receives its ID, name, and template, and before
  `mount()` or hydration. Public properties therefore still hold their class defaults, also during updates.
- **Order.** Modifiers run in the order of the array, as merged by Magento. There is no sort order.
- **Changing arguments.** Use `merge()` on the arguments. `set()` does not overwrite an existing key, and `put()`
  does not add a missing one.
- **Validation.** The argument must be an array, and every item must implement `ModifierInterface`; otherwise an
  `InvalidArgumentException` is thrown. An item therefore cannot be switched off with `xsi:type="null"` in a later
  layout file.
- **Instances.** Declare items with `shared="false"` when a modifier keeps state.

The interface extends Magento's `ArgumentInterface`, so layout XML can pass modifiers as `xsi:type="object"`
arguments.

## How the arguments reach the component

The layout resolver collects every block data key of the form `magewire:<name>`, with exactly one colon, as a
top-level argument in camel case: `magewire:listeners` becomes `listeners`. The built-in resolvers inherit this
behavior. A [custom resolver](../advanced/architecture/mechanisms/resolvers.md) supports these arguments only when
its `arguments()` object collects them from the block.

The build steps are:

1. the resolver collects the block's arguments;
2. the component receives its block, resolver, and layout lifecycle;
3. modifiers run;
4. the resolver assembles the component (ID, name, alias, and template);
5. the `magewire:component:build` hook fires;
6. `mount()` runs on the first render, or the snapshot is hydrated on an update.

## Related

- [Events](../essentials/events.md): listeners and dispatching.
- [Magewire Loaders](../advanced/javascript/features/magewire-loaders.md): loader keys and messages.
- [Components](../essentials/components.md#advanced-block-arguments): other block arguments.
- [Resolvers](../advanced/architecture/mechanisms/resolvers.md): how components are built from layout.
