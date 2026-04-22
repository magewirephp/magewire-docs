# Features

{{ include('admonition/livewire-concept.md') }}

Magewire is divided into three aspects. First, there is the architecture itself, which includes the module responsible
for loading everything within Magento, as well as specific Livewire concepts. Those other two aspects within this architecture
are **Features** and **Mechanisms**.

In this documentation, we will focus specifically on **Features**.

## Concept

The idea behind Features is that they are primarily optional and can be disabled without affecting the core principles of Magewire.
In that sense, they are considered nice-to-haves.

Any third-party additions to Magewire will mainly come in the form of Features and can be integrated separately through other modules.

## Example

We use **Directives** as an example.

Magewire Directives allow you to add directives prefixed with `@` within Magewire-driven block templates.
These directives use bound parsers to transform them into a specific output.

For instance, consider `@ucfirst('foo')`, which would render as `Foo`.

Now, you might wonder: *If I disable this feature, won't `@ucfirst` just appear as plain text in my template?*
That’s correct—but it won’t break the architecture, and everything else will continue to function as expected.

So, while in this particular example, you would likely never want to disable or remove **Directives**, the possibility still exists.

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
                <item name="magewire_compiling" xsi:type="array">
                    <item name="type" xsi:type="string">
                        Magewirephp\Magewire\Features\SupportMagewireCompiling\SupportMagewireCompiling
                    </item>
                    <item name="sort_order" xsi:type="number">99100</item>
                    <!-- Optional. Defaults to the Features fallback (LAZY = 10). -->
                    <item name="boot_mode" xsi:type="number">30</item>
                </item>
            </argument>
        </arguments>
    </type>
</config>
```

Each `<item>` in the `items` array carries:

- `type` — fully-qualified class name of the feature (must extend `ComponentHook`).
- `sort_order` — required; lower numbers boot first. Core features occupy 700 – 99900; pick a slot relative to the features yours depends on.
- `boot_mode` — optional; integer from the `ServiceTypeItemBootMode` enum (`LAZY = 10`, `PERSISTENT = 20`, `ALWAYS = 30`). Omit to inherit the Features fallback.

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
For complete details on implementing JavaScript features, refer to the [Features JavaScript](../javascript/index.md#features) paragraph.

### Hooks

The Livewire (and by extension, Magewire) architecture was designed with extensibility in mind, allowing developers to hook into processes before or after they occur.

Listeners are registered via `Magewirephp\Magewire\on($event, $callback)`. Two rules:

- A listener's return value is either a **callback** (the "after" half of the hook) or the incoming value unchanged. Returning a callback turns the listener into before/after middleware — the callback receives the downstream return value, can mutate it, and must return a result.
- When a listener returns a callback, the result is automatically piped into it — modify it if you need to, but always return a result to keep the pipeline consistent.

#### FAQ

| Question | Answer |
|---|---|
| When do I use hooks? | When you need to react to specific Magewire lifecycle events (construct, mount, hydrate, update, call, render, dehydrate, destroy, exception, …) or trigger your own events that other code listens for. |
| Are these hooks the same as Observer Events? | No. Hooks are an in-process, closure-based middleware pipeline — faster, typed, and able to run before/after semantics with return values. Observer Events are Magento's dispatched-event system. Magewire **also** ships `SupportMagentoObserverEvents` (registered by default in frontend and adminhtml), which re-emits every Magewire lifecycle event as a Magento observer event prefixed `magewire_on_*`. Non-alphanumeric characters in the event name are replaced with `_`, so `magewire:component:construct` becomes `magewire_on_magewire_component_construct`, `render` becomes `magewire_on_render`, etc. Reach for a hook when you want middleware semantics; reach for an observer when you want Magento-native extensibility. |

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
            // Before — runs in place of the "before" half of the hook.

            return function (string $html): string {
                // After — receives the rendered HTML, can mutate, must return.
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
            // Before — runs immediately when the event fires.

            return function (AbstractBlock $block): AbstractBlock {
                // After — runs when the pipeline unwinds with the downstream result.
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

`trigger()` returns a callable that fans out to every registered "after" callback, walking the pipeline in reverse registration order. The listener receives the block, performs its "before" work, and returns a callback that is invoked with the block once the rest of the pipeline has completed.

## Related

- [Component Hooks](component-hooks.md) — full list of lifecycle events and the hook-registration contract.
- [Mechanisms](mechanisms/index.md) — what Features register alongside.
