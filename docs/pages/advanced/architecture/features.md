# Features

{{ include('admonition/livewire-concept.md') }}

Magewire is divided into three aspects. First, there is the architecture itself, which includes the module responsible
for loading everything within Magento, as well as specific Livewire concepts. Those other two aspects within this architecture
are **Features** and **Mechanisms**.

In this documentation, we will focus specifically on **Features**.

## Concept

Features are smaller lifecycle capabilities than Mechanisms, but they are not all optional in practice. Notifications
and project-specific hooks can be removed when nothing uses them. Lifecycle hooks, events, and several other
registered Features are required for the documented component runtime. Do not disable a core Feature solely because
it is categorized as a Feature.

Any third-party additions to Magewire will mainly come in the form of Features and can be integrated separately through other modules.

## Example

Notifications and rate limiting are examples of features. Template compilation is not: it moved to the required `HandleCompiling` mechanism in Magewire 3.3.

## Write your own

Create a class that extends `Magewirephp\Magewire\ComponentHook` and declare a `provide()` method. Inside `provide()`, subscribe to any events you need via `Magewirephp\Magewire\on(…)`. Then register the class on the Features service type in area-scoped DI.

```xml title="File: etc/frontend/di.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:ObjectManager/etc/config.xsd"
>
    <type name="Magewirephp\Magewire\Features">
        <arguments>
            <argument name="items" xsi:type="array">
                <item name="vendor_example" xsi:type="array">
                    <item name="type" xsi:type="string">
                        Vendor\Module\Magewire\Features\SupportExample\SupportExample
                    </item>
                    <item name="sort_order" xsi:type="number">6000</item>
                    <!-- Optional. Defaults to the Features fallback (LAZY = 10). -->
                    <item name="boot_mode" xsi:type="number">30</item>
                </item>
            </argument>
        </arguments>
    </type>
</config>
```

Each `<item>` in the `items` array carries:

- `type`: fully-qualified class name of the feature (must extend `ComponentHook`).
- `sort_order`: required; lower numbers boot first. Pick a slot relative to the features yours depends on and recheck the tagged area-specific DI configuration on upgrades.
- `boot_mode`: optional; integer from the `ServiceTypeItemBootMode` enum (`LAZY = 10`, `PERSISTENT = 20`, `ALWAYS = 30`). Omit to inherit the Features fallback.

Register under `etc/adminhtml/di.xml` as well if the feature must run in the admin area.

### Module structure

We encourage everyone to use the `src/` root folder within your module for all Magewire-related code.
Components should reside directly in this folder or be organized into subdirectories.
Features should also be placed within `src/`, using a `Features/` folder.

Each feature should be grouped inside a `Support`-prefixed subfolder, which contains everything related to that feature.

As a general rule within the core, feature naming follows a prefix convention:

- If it's a Magewire-specific feature, prefix it with `SupportMagewire`.
- If it's intended to make a Magento feature compatible with Magewire, use the `SupportMagento` prefix.

This isn't a strict requirement, but it’s considered a best practice for consistency.

### JavaScript

You can extend your feature to the frontend by adding JavaScript functionality when required.

This JavaScript code doesn't live within the feature folder itself, but must be organized within the `/view` subfolder structure.
For complete details on implementing JavaScript features, refer to the [JavaScript](../javascript/index.md) page.

### Hooks

The Livewire (and by extension, Magewire) architecture was designed with extensibility in mind, allowing developers to hook into processes before or after they occur.

Listeners are registered via `Magewirephp\Magewire\on($event, $callback)`. Two rules:

- A listener can return a **callback** for the later phase of the event. The code that triggered the event decides when
  to invoke the returned dispatcher and which value to pass forward.
- Finish callbacks run in registration order. When a callback returns a value, that value becomes the input for the
  next callback. This is a forward pipeline, not a reverse middleware unwind.

#### FAQ

| Question | Answer |
|---|---|
| When do I use hooks? | When you need to react to specific Magewire lifecycle events (construct, mount, hydrate, update, call, render, dehydrate, destroy, exception, …) or trigger your own events that other code listens for. |
| Are these hooks the same as Observer Events? | No. Hooks are an in-process callback pipeline with before/later phases and return values. Observer Events are Magento's dispatched-event system. Magewire ships `SupportMagentoObserverEvents`, which maps a fixed list of core events to names prefixed with `magewire_on_*`. It is not a wildcard bridge for every custom event. Non-alphanumeric characters become `_`, so `magewire:component:construct` becomes `magewire_on_magewire_component_construct`. |

#### Observer event example

```xml title="etc/frontend/events.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Event/etc/events.xsd">
    <event name="magewire_on_render">
        <observer name="my_module_magewire_on_render"
                  instance="Vendor\Module\Observer\MagewireOnRender"/>
    </event>
</config>
```

```php title="Vendor/Module/Observer/MagewireOnRender.php"
use Magewirephp\Magewire\Component;
use Magewirephp\Magewire\Features\SupportMagentoObserverEvents\DTO\ListenerDataTransferObject;

class MagewireOnRender implements \Magento\Framework\Event\ObserverInterface
{
    public function execute(\Magento\Framework\Event\Observer $observer): void
    {
        /** @var ListenerDataTransferObject $listener */
        $listener = $observer->getData('listener');

        $listener->with(function (Component $component, $block) {
            // Before: runs in place of the "before" half of the hook.

            return function (string $html): string {
                // After: receives the rendered HTML, can mutate, must return.
                return $html;
            };
        });
    }
}
```

#### Hook example

```php title="Magewire/Features/SupportExample/SupportExample.php"
<?php

namespace Vendor\Module\Magewire\Features\SupportExample;

use Magento\Framework\View\Element\AbstractBlock;
use Magewirephp\Magewire\ComponentHook;

use function Magewirephp\Magewire\on;

class SupportExample extends ComponentHook
{
    public function provide(): void
    {
        on('magewire:component:construct', function (AbstractBlock $block) {
            // Before: runs immediately when the event fires.

            return function (AbstractBlock $block): AbstractBlock {
                // Later phase: runs when the caller invokes the returned dispatcher.
                return $block;
            };
        });
    }
}
```

The event is emitted in core via:

```php
$construct = trigger('magewire:component:construct', $block);
$block = $construct();
```

`trigger()` calls the registered listeners immediately and returns a dispatcher for the callbacks they returned.
When the caller invokes that dispatcher, finish callbacks run in registration order and pass any returned value
forward to the next callback.

## Related

- [Component Hooks](component-hooks.md): full list of lifecycle events and the hook-registration contract.
- [Mechanisms](mechanisms/index.md): what Features register alongside.
