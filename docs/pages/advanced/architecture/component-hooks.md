# Component Hooks

{{ include('admonition/livewire-concept.md') }}

A **Component Hook** is a class that subscribes to events in the Magewire request pipeline. Hooks are the mechanism behind every built-in Feature — notifications, redirects, rate limiting, backwards compatibility — and are the intended extension point for custom framework-level behaviour.

Unlike lifecycle hooks on a component class (which only see their own component), a Component Hook sees **every** component in the pipeline.

## Anatomy

Extend `Magewirephp\Magewire\ComponentHook` and implement `provide()`. Inside `provide()`, register listeners with `Magewirephp\Magewire\on(…)`.

```php title="Vendor/Module/Magewire/Hooks/SupportLogRender.php"
<?php

namespace Vendor\Module\Magewire\Hooks;

use Magewirephp\Magewire\Component;
use Magewirephp\Magewire\ComponentHook;
use Magento\Framework\View\Element\AbstractBlock;

use function Magewirephp\Magewire\on;

class SupportLogRender extends ComponentHook
{
    public function __construct(
        private \Psr\Log\LoggerInterface $logger
    ) {}

    public function provide(): void
    {
        on('render', function (Component $component, AbstractBlock $block) {
            $started = microtime(true);

            return function (string $html) use ($component, $started): string {
                $this->logger->debug(sprintf(
                    'Magewire: %s rendered in %.1fms',
                    $component::class,
                    (microtime(true) - $started) * 1000,
                ));

                return $html;
            };
        });
    }
}
```

## Before vs. after (middleware pattern)

`on('event', $callback)` is a middleware. The behaviour depends on what `$callback` returns:

| Return value | Runs as |
|---|---|
| `null` / nothing | Before-only listener |
| `Closure` | Before + after. The closure receives the downstream return value, can mutate it, and must return. |

```php
on('dehydrate', function (Component $component, array $snapshot): \Closure {
    // Before — inspect the component before snapshot finalises.

    return function (array $snapshot): array {
        // After — mutate the snapshot before it leaves the server.
        $snapshot['memo']['customFlag'] = true;
        return $snapshot;
    };
});
```

## Registering a hook

Register the hook class on the `Magewirephp\Magewire\Features` collection in area-scoped DI — never global `etc/di.xml`:

```xml title="etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Features">
    <arguments>
        <argument name="items" xsi:type="array">
            <item name="support_log_render" xsi:type="array">
                <item name="type" xsi:type="string">
                    Vendor\Module\Magewire\Hooks\SupportLogRender
                </item>
                <item name="sort_order" xsi:type="number">10000</item>
                <item name="boot_mode" xsi:type="number">30</item>
            </item>
        </argument>
    </arguments>
</type>
```

The `Features` collection calls `provide()` on the hook when it registers, giving it a chance to subscribe to events. Register on `Magewirephp\Magewire\Mechanisms` instead when the hook is framework-critical and must boot before Features. Register in `adminhtml/di.xml` too if the hook is needed in the admin area.

## Events

### Lifecycle

| Event | Fires |
|---|---|
| `magewire:component:construct` | Component instantiated during initial page load |
| `magewire:component:reconstruct` | Component instantiated during an update roundtrip |
| `magewire:component:build` | Component has been fully built |
| `pre-mount` | Before `mount()` runs |
| `mount.stub` | Placeholder mount step |
| `mount` | `mount()` completes |
| `hydrate` | Component hydrated from snapshot |
| `update` | Property update applied |
| `call` | Public method invoked |
| `render` | Template about to render |
| `render.placeholder` | Placeholder render step |
| `dehydrate` | Snapshot being written |
| `destroy` | Component finalising |

Signatures vary per event and evolve between releases — inspect the emit site in core (grep for `trigger('event-name'`) for the exact arguments.

### Request / response

| Event | Fires |
|---|---|
| `request` | Update controller received a request |
| `response` | Response is about to be sent |
| `exception` | Uncaught exception escaped the component |
| `flush-state` | State is being flushed |
| `profile` | Profiling event |

### Checksum

| Event | Fires |
|---|---|
| `checksum.generate` | Generating an outgoing snapshot HMAC |
| `checksum.verify` | Verifying an incoming snapshot HMAC |
| `checksum.fail` | Verification failed |
| `snapshot-verified` | Verification succeeded |

### Morph

Emitted on the JS side and available via `Magewire.hook(…)`:

`morph.updating`, `morph.removed`, `element.init`, `component.init`, `commit`.

## Magento Observer bridge

For listeners that do not need closure-based middleware semantics, Magewire re-emits lifecycle events as Magento observer events prefixed `magewire_on_`. Dots in the event name become underscores (`magewire:construct` → `magewire_on_construct`).

```xml title="etc/frontend/events.xml"
<event name="magewire_on_render">
    <observer name="MagewireOnRender"
              instance="Vendor\Module\Observer\Frontend\MagewireOnRender" />
</event>
```

```php
class MagewireOnRender implements \Magento\Framework\Event\ObserverInterface
{
    public function execute(\Magento\Framework\Event\Observer $observer): void
    {
        /** @var \Magewirephp\Magewire\Features\SupportMagentoObserverEvents\DTO\ListenerDataTransferObject $listener */
        $listener = $observer->getData('listener');

        $listener->with(function (Component $component, AbstractBlock $block) {
            return function (string $html): string {
                return $html;
            };
        });
    }
}
```

Prefer Component Hooks for most work — they are faster (no observer dispatch), typed, and area-scoped.

## Component Hook vs. Feature

A **Feature** is a Component Hook with a name and a layout footprint — it typically owns PHTML, CSS, or JS assets rendered into `magewire.features` and friends. A Component Hook is the smaller primitive. Every Feature contains at least one hook class; a hook class without layout assets does not need Feature packaging.

See [Features](features.md).

## Related

- [Mechanisms](mechanisms/index.md)
- [Features](features.md)
- [Lifecycle Hooks](../../essentials/lifecycle-hooks.md) — per-component lifecycle.
