# Magewire Loaders

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Magewire loaders connect a component update to the notifier addon. The notification appears when a configured action or
property update starts, keeps its loader active while the commit is in flight, and stops it on success or failure.

This is separate from [`wire:loading`](../../../html-directives/wire-loading.md), which changes an element inside the
component template. Use `wire:loading` for local button and form state; use a Magewire loader when the interaction needs
a page-level notification.

## Configuring action loaders

Declare a protected `$loader` map on the component. Each key selects an action and each value contains one or more
customer-visible messages:

```php title="Magewire/Counter.php"
<?php

declare(strict_types=1);

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Component;

class Counter extends Component
{
    public int $count = 0;

    protected $loader = [
        'increment' => 'Updating counter…',
    ];

    public function increment(): void
    {
        $this->count++;
    }
}
```

Loader strings are passed through Magento translation during dehydration. The current action matcher accepts:

| Key | Matches |
|---|---|
| `save` | The exact method name. |
| `account.save` | An exact dotted method expression. |
| `account` | A parent segment of a dotted expression. |
| `*` | Any method call on the component. |

Prefer exact action names. A wildcard can generate noisy notifications for internal or incidental calls.

## Message sequences

A value may be one string or an array of strings:

```php
protected $loader = [
    'save' => 'Saving ... Saved.',
    'publish' => [
        'Publishing ... Published.',
        'Catalog: Refreshing index',
    ],
];
```

The loader utility recognizes a small message grammar:

| Message | Behavior |
|---|---|
| `Saving` | Show one loading notification. |
| `Saving ... Saved` | Show `Saving` during the request and `Saved` after success. |
| `... Saved` | Show no initial message and create `Saved` after success. |
| `Catalog: Refreshing` | Use `Catalog` as the notification title. |

The follow-up part is created only after a successful commit. On failure, the active loader is stopped without showing
the success message. Three literal periods form the separator; the Unicode ellipsis character does not.

## Property update loaders

The same map can target updates produced by `wire:model.live`, `$wire.set()`, or another property mutation:

```php
protected $loader = [
    'status' => 'Changing {previous_value} to {value}…',
    'status:active' => 'Activating account…',
    'profile.name' => 'Updating profile name to {value}…',
];
```

Property matching proceeds from the most specific expression to broader forms: an exact `property:value` pair, a
parent/value or final-segment/value pair for nested properties, then the exact property, parent, or final segment.

`{value}` and `{previous_value}` are replaced in property messages in the browser. They are notification text only;
never treat them as escaped HTML or trusted state.

## Fast-request suppression

The browser records recent completion times per component and action in `sessionStorage`. After at least two samples,
it suppresses the spinner when the median duration is below 300 ms. The notification can still appear, but without an
active loader. This avoids flashing a spinner for interactions that consistently finish almost immediately.

Timings are browser-local heuristics, not performance telemetry. Use server profiling and the browser network panel for
real measurements.

## Custom behavior with hooks

For behavior that cannot be expressed by the map, listen to Magewire's commit hook and call the notifier directly:

```javascript
document.addEventListener('magewire:init', () => {
    Magewire.hook('commit', ({ commit, succeed, fail }) => {
        const updatesCounter = commit.calls.some(({ method }) => method === 'increment')

        if (! updatesCounter) {
            return
        }

        succeed(() => window.MagewireAddons.notifier.create('Counter updated'))
        fail(() => window.MagewireAddons.notifier.create('Counter update failed', {
            type: 'error',
        }))
    })
}, { once: true })
```

The notifier addon is registered by Magewire's default layout. If a theme or compatibility module removes that addon,
the loader feature has no notification surface. See [Magewire Notifier](../addons/magewire-notifier.md) and the
[Loader Utility](../utilities/loader.md) for the underlying JavaScript APIs.
