# Performance

Magewire components are cheap — a typical round-trip is a small JSON payload, a PHP re-render of one block, and a DOM morph. Performance problems are almost always about doing too many round-trips, not about any single round-trip being slow.

## Reduce round-trips

### Choose the right `wire:model` modifier

| Pattern | Choice |
|---|---|
| User types, server reacts on save only | `wire:model` (deferred) |
| Live filter / search | `wire:model.live.debounce.250ms` |
| Expensive validation, react when user pauses | `wire:model.blur` |

`wire:model.live` without debounce hits the server on every keystroke. Use the 250–500 ms debounce unless you have a concrete reason not to.

### Scope `wire:poll`

`wire:poll="refresh"` with no interval defaults to **2 seconds**. On a page with 10 polling components across 1 000 users, that's 5 000 req/s.

- Use an explicit interval: `wire:poll.30s="refresh"`.
- Add `.visible` so off-screen widgets stop polling.
- Drop polling entirely when an event-driven `$this->dispatch()` will do.

### Bundle updates on the client

Multiple `$wire.set()` / `$wire.call()` calls within the same browser tick are [bundled](../features/request-bundling.md) into a single request automatically. Two separate clicks fired 10 ms apart are two requests. If that cost matters, batch the intent into one action.

## Reduce server cost

### `skipRender()`

An action that mutates state the UI does not reflect (a log entry, a background-queue enqueue, a redirect) does not need to re-render. Call `$this->skipRender()` — Magewire skips the template render and sends only the effects.

```php
public function logClick(): void
{
    $this->analytics->trackClick();
    $this->skipRender();
}
```

### Minimise public properties

Every `public` property is serialised on every request. A 500 kB array on a polling component is 500 kB × poll-rate of bandwidth wasted.

- Keep large read-only data in a private property, hydrated in `boot()` from cache or DB.
- Summarise — send a count or a list of IDs, look up details on demand.

### Lazy boot

Boot modes are defined by the `Magewirephp\Magewire\Enums\ServiceTypeItemBootMode` enum: `LAZY = 10`, `PERSISTENT = 20`, `ALWAYS = 30`. The enum-wide default is `ALWAYS`, but `Features` and `Mechanisms` fall back to `LAZY` when a registration omits `boot_mode`; the core ships most items at `ALWAYS` (30). For rarely-triggered behaviour, drop an item to `LAZY`:

```xml
<item name="boot_mode" xsi:type="number">10</item>
```

Set this inside the `<item>` definition when registering a Feature or Mechanism in area-scoped `di.xml` — see `src/etc/frontend/di.xml` for examples.

### Avoid work in `render()` / `rendering()` hooks

`render()` runs every time the component re-renders. Computing expensive derived state there means paying on every round-trip. Cache the derivation in a property computed in `boot()` or `updated*()` and read the property from the template.

## Reduce round-trip size

### `wire:loading.delay`

A 100 ms request followed by a visible "Loading…" state creates jank. `wire:loading.delay` waits 200 ms before showing the indicator — so fast requests feel instantaneous and only slow ones surface a loading state.

```html
<span wire:loading.delay>Working…</span>
```

### Keyed loops

An unkeyed loop over 200 items forces the morph algorithm to replace every node on any change. A keyed loop matches nodes by `wire:key` and moves or mutates only what changed. Always key loops.

### `wire:ignore` for heavy subtrees

Third-party widgets (date pickers, Google Maps, rich-text editors) are expensive to re-hydrate on every morph. Wrap them in `wire:ignore` — Magewire walks past the subtree and the browser keeps the existing DOM.

## Monitoring

- **Magento FPC**: Magewire adds a cache-bypass header on update responses. The GET that renders the initial component is still FPC-cacheable — check that your block's FPC handle is configured correctly.
- **Browser devtools**: in the Network tab, filter for `magewire/update`. Sort by duration. The slow requests tell you which actions are hot.
- **System log**: enabled rate limiting surfaces per-component hot spots. Check `var/log/system.log` for `MagewireRateLimit` entries.

## Related

- [Request bundling](../features/request-bundling.md)
- [wire:poll](../html-directives/wire-poll.md)
- [wire:loading](../html-directives/wire-loading.md)
- [Best practices](best-practices.md)
