# Magento Observer Events

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Magewire has its own in-process event pipeline (`on()` / `trigger()`) that powers
[Component Hooks](component-hooks.md). That pipeline is fast and typed, but it's *Magewire's* — to
listen, you write a Mechanism, Feature, or hook.

The `SupportMagentoObserverEvents` feature bridges that pipeline into **Magento's native observer
system**, so you can react to a component's lifecycle from a plain `events.xml` observer — no
Magewire-specific class required.

## How it works

For every event in its map, the feature registers an `on()` listener that re-dispatches the event as
a Magento event named:

```
magewire_on_<event>
```

…where `<event>` is the original name with every non-alphanumeric character replaced by `_`. So:

| Magewire event | Magento observer event |
|---|---|
| `mount` | `magewire_on_mount` |
| `render` | `magewire_on_render` |
| `dehydrate` | `magewire_on_dehydrate` |
| `magewire:component:construct` | `magewire_on_magewire_component_construct` |
| `magento:block:render` | `magewire_on_magento_block_render` |
| `checksum.fail` | `magewire_on_checksum_fail` |

## Observable events

The feature maps the full lifecycle. The notable ones:

- **Magewire-specific:** `magewire:component:construct`, `magewire:component:reconstruct`,
  `magewire:component:build`, `magewire:view:compile`, `magewire:setup`, `magewire:boot`.
- **Magento-specific:** `magento:block:render`, `magento:block:rendered`, `magento:template:render`.
- **Component lifecycle:** `pre-mount`, `mount.stub`, `mount`, `hydrate`, `update`, `call`, `render`,
  `render.placeholder`, `dehydrate`, `destroy`.
- **Request/response:** `request`, `response`.
- **Checksum:** `checksum.generate`, `checksum.verify`, `checksum.fail`, `snapshot-verified`.
- **Magic methods:** `__get`, `__unset`, `__call`.
- **Utility:** `exception`, `flush-state`, `profile`.

## Listening from an observer

Register an observer against the `magewire_on_*` event as usual:

```xml title="etc/frontend/events.xml"
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Event/etc/events.xsd">
    <event name="magewire_on_mount">
        <observer name="vendor_module_on_magewire_mount"
                  instance="Vendor\Module\Observer\OnMagewireMount"/>
    </event>
</config>
```

The observer doesn't receive the Magewire arguments directly. Instead it's handed a **listener**
object on which you register a callback — the callback then receives the original event arguments:

```php
namespace Vendor\Module\Observer;

use Magento\Framework\Event\Observer;
use Magento\Framework\Event\ObserverInterface;
use Magewirephp\Magewire\Component;

class OnMagewireMount implements ObserverInterface
{
    public function execute(Observer $observer): void
    {
        $listener = $observer->getData('listener');

        $listener->with(function (Component $component) {
            // Runs with the same arguments the 'mount' event fired with.
        });
    }
}
```

### Before / after semantics

If your callback **returns another callable**, that returned function runs as an *after* step — the
same before/after middleware shape Magewire's own hooks use. Returning nothing simply reacts at the
"before" point:

```php
$listener->with(function (Component $component) {
    // before

    return function ($result) {
        // after — receives the event result, can transform and return it
        return $result;
    };
});
```

When several observers each contribute an after step, they run as a pipeline.

## When to use this vs Component Hooks

| Reach for… | When |
|---|---|
| [Component Hooks](component-hooks.md) | You want middleware semantics, typed access, and return values inside Magewire. |
| **Observer events** | You want Magento-native extensibility — a third party reacting to Magewire without depending on Magewire's hook classes. |

Hooks are the in-framework tool; observer events are the Magento-ecosystem door onto the same
lifecycle.

## Related

- [Component Hooks](component-hooks.md) — the underlying `on()` / `trigger()` pipeline.
- [Runtime](runtime.md) — where `magewire:setup` / `magewire:boot` fire.
- [Features](features.md) — how this feature is registered.