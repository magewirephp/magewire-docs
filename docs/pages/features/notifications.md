# Notifications

Notifications send toast-style messages from a component response to the registered notifier addon.

```php
$this->magewireNotifications()
    ->make(__('Saved.'))
    ->asSuccess();
```

`make()` expects a Magento `Phrase`, so use `__()` for translatable customer-facing text.

## Builder API

| Method | Effect |
|---|---|
| `make(Phrase $message, ?string $name = null)` | Create a notification, or return the already-created builder item with the same name. |
| `asSuccess()` / `asError()` / `asWarning()` / `asNotice()` | Select a standard message type. |
| `as(NotificationType $type)` | Select a notification enum value directly. |
| `withMessage(Phrase $message)` | Change the message on the builder item. |
| `withTitle(Phrase $title)` / `withoutTitle()` | Set or remove a title. |
| `withDuration(int $milliseconds)` | Set the browser display duration. The PHP default is 3000 ms. |

```php
$this->magewireNotifications()
    ->make(__('Order %1 confirmed.', $orderId), 'order-confirmation')
    ->asSuccess()
    ->withTitle(__('Order confirmation'))
    ->withDuration(5000);
```

## Named notifications

Names de-duplicate notifications within the current builder collection. Calling `make()` again with the same name returns the existing item; it does not automatically replace its message or type. Update that item through the fluent methods:

```php
$notification = $this->magewireNotifications()
    ->make(__('Saving…'), 'save-progress')
    ->asNotice();

// Later in the same response-building flow:
$this->magewireNotifications()
    ->make(__('Ignored because the name already exists.'), 'save-progress')
    ->withMessage(__('Saved.'))
    ->asSuccess();
```

## JavaScript access

```javascript
document.addEventListener('magewire:init', async () => {
    await window.MagewireAddons.notifier.create('Saved.', {
        type: 'success',
        duration: 3000,
    })
}, { once: true })
```

See [Magewire Notifier](../advanced/javascript/addons/magewire-notifier.md) for lifecycle methods and hooks.
