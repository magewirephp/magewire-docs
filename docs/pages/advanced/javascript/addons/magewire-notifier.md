# Magewire Notifier

Notification management for displaying user messages.

```js
document.addEventListener('magewire:init', event => {
    const { addons } = event.detail.magewire;
    const message = 'Foo';
    
    addons.notifier.create(message, { duration: 50000 }, {
        onActivate: notification => console.log('Notification activated.')
    }).then(notification => {
        console.log('Notification created.')
    }).catch(exception => {
        console.log('Notification', message)
    })
})
```

## Elements

| Description      | File                                                               |
|------------------|--------------------------------------------------------------------|
| Magewire Addon   | view/base/templates/js/magewire/addons/notifier.phtml              |
| Alpine Component | view/base/templates/js/alpinejs/components/magewire-notifier.phtml |
| UI Component     | view/base/templates/magewire/ui-components/notifier.phtml          |

## Methods

### `async create`

Create a new notification and optionally activate it immediately.

**Arguments:**

- `message` (string) - The message content to display in the notification.
- `options` (object, optional) - Configuration options for the notification:
    - `type` (string, optional) - Notification type: `'success'`, `'error'`, `'warning'`, `'info'`. Default: `'info'`.
    - `title` (string, optional) - Notification title. Default: `'Message Unknown'` (i18n).
    - `duration` (number, optional) - Display duration in milliseconds. Default: `3600`.
    - `recoverable` (bool, optional) - Can be recovered and will trigger the `onRecover` hook.
- `hooks` (object, optional) - Event callback functions that will be triggered during the notification lifecycle:
    - `onActivate({ notification })` (function, optional) - Called when notification is activated.
    - `onCleanup({ notification })` (function, optional) - Called during cleanup process.
    - `onTermination({ notification })` (function, optional) - Called when notification is terminated.
    - `onRecover({ notification })` (function, optional) - Called when notification encounters an error.
    - `onStateChange({ notification })` (function, optional) - Called when notification encounters an error.
    - `onFailure({ notification, reason })` (function, optional) - Called when notification encounters an error.
- `activate` (boolean, optional) - Whether to automatically activate the notification upon creation. Default: `true`.

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', async event => {
    const notification = await create(
        // Message
        'Task completed successfully',
        
        // Options
        { type: 'success', duration: 5000 },
        
        // Hooks
        { onFinish: notification => console.log('Done!') },
        
        // Activate
        true
    );
})
```

### `get`

Returns a notification.

**Arguments:**

- `id` (number) - Notification ID.

**Returns:** `object<Notification>|null`

```js
document.addEventListener('magewire:init', event => {
    const notification = Magewire.addons.notifier.get(1);
})
```

### `async activate`

Activates a notification.

**Arguments:**

- `id` (number) - Notification ID.

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.activate(1);
})
```

### `async finish`

Flags a notification as finished.

For example after a loading process has completed.

**Arguments:**

- `id` (number) - Notification ID.

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.finish(1);
})
```

### `async terminate`

Flags a notification as terminated, making it inactive.

**Arguments:**

- `id` (number) - Notification ID.

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.terminate(1);
})
```

### `async fail`

Flags a notification as failed.

**Arguments:**

- `id` (number) - Notification ID
- `reason` (string, optional) - Failure reason. Default: `null`

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.fail(1);
})
```

### `async hold`

Clears the active notification timeout.

**Arguments:**

- `id` (number) - Notification ID

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.hold(1);
})
```

### `async fetch`

Returns all notifications.

**Returns:** `Array<int, Notification>`

```js
document.addEventListener('magewire:init', event => {
    const notifications = Magewire.addons.notifier.fetch();
})
```

### `async trigger`

Triggers hooks on a global and an item level when available.

**Arguments:**

- `hook` (string) - Hook name
- `args` (object, optional) - Hook arguments. Default: `{}`
- `notification` (object, optional) - Existing notification object. Default: `null`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.trigger('foo', { bar: 'baz' }, null);
})
```

## Events

Hooking into several notifier events can be achieved like so:

```js
document.addEventListener('magewire:init', () => {
    Magewire.hook('addons.notifier.state-change', ({ state, previous, notification }) => {
        console.log(`Notification state changed from ${state} to ${previous}`, notification);
    });
});
```

### Available Events
| Event                        | Arguments                           |
|------------------------------|-------------------------------------|
| addons.notifier.activate     | `{ notification }`                  |
| addons.notifier.cleanup      | `{ notification }`                  |
| addons.notifier.terminate    | `{ notification }`                  |
| addons.notifier.recover      | `{ notification }`                  |
| addons.notifier.state-change | `{ state, previous, notification }` |
| addons.notifier.failure      | `{ notification, reason }`          |

!!! tip "Use `Magewire.addons.notifier.create()` to define notification-specific hooks for individual notifications. Use global hooks to respond to lifecycle events across all notifications."
