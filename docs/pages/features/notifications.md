# Notifications

Surface toast-style messages to the user from inside a component action. Notifications travel back as effects on the next response and are rendered by the notifier Alpine component in `magewire.ui-components`.

```php
$this->magewireNotifications()
    ->make(__('Saved.'))
    ->asSuccess();
```

## Builder API

`magewireNotifications()` returns a fluent builder.

| Method | Effect |
|---|---|
| `make($message)` | Start a new notification with the given message |
| `asSuccess()` | Green success style |
| `asError()` | Red error style |
| `asWarning()` | Amber warning style |
| `asNotice()` | Neutral info style |
| `withTitle($title)` | Add a title above the message |
| `withDuration($ms)` | Auto-dismiss after `$ms` milliseconds (default 3000) |

```php
$this->magewireNotifications()
    ->make(__('Order %1 confirmed.', $orderId))
    ->asSuccess()
    ->withTitle(__('Order Confirmation'))
    ->withDuration(5000);
```

## Named notifications

Pass a name as the second argument to `make()` to prevent duplicates. Firing the same-named notification while one is still visible replaces the existing instance rather than stacking.

```php
$this->magewireNotifications()
    ->make(__('Saving…'), 'save-progress')
    ->asNotice()
    ->withDuration(0);  // 0 = sticky, no auto-dismiss

// Later, when save completes:
$this->magewireNotifications()
    ->make(__('Saved.'), 'save-progress')
    ->asSuccess();
```

## Rendering

The notifier is registered under `magewire.ui-components`. Theme modules can override its template or style it via CSS variables (see [Tailwind](../theming/tailwind.md)).

For programmatic access from JavaScript, the notifier exposes an addon:

```javascript
window.MagewireAddons.notifier.create('Hello', {
    type: 'success',
    duration: 3000,
});
```

`create(message, options, hooks)` takes the message string as the first argument; `options` accepts `type`, `duration`, `title`, and the per-notification lifecycle hooks (`onCreate`, `onActivate`, `onCleanup`, `onTerminate`, `onStateChange`, `onClick`, `onFailure`).

See [Magewire Notifier](../advanced/javascript/addons/magewire-notifier.md) for the JS surface.

## Related

- [Actions](../essentials/actions.md)
- [Magewire Notifier (JS addon)](../advanced/javascript/addons/magewire-notifier.md)
- [Tailwind](../theming/tailwind.md) — notifier CSS variables.
