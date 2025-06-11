# Magewire Notifier

Notification management for displaying user messages.

```js
document.addEventListener('magewire:init', event => {
    const { addons } = event.detail.magewire;
    const message = 'Foo';
    
    addons.notifier.create(message, { duration: 50000 }, {
        onActivation: notification => console.log('Notification activated.')
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
- `hooks` (object, optional) - Event callback functions that will be triggered during the notification lifecycle:
    - `onTermination(notification)` (function, optional) - Called when notification is terminated.
    - `onActivation(notification)` (function, optional) - Called when notification is activated.
    - `onFailure(notification, reason)` (function, optional) - Called when notification encounters an error.
    - `onCleanup(notification)` (function, optional) - Called during cleanup process.
    - `onFinish(notification)` (function, optional) - Called when notification completes successfully.
- `activate` (boolean, optional) - Whether to automatically activate the notification upon creation. Default: `true`.

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', async event => {
    const notification = await create(
        'Task completed successfully',
        { type: 'success', duration: 5000 },
        { onFinish: notification => console.log('Done!') },
        true
    );
})
```

## `get`

Returns a notification.

**Arguments:**

- `id` (number) - Notification ID.

**Returns:** `object<Notification>|null`

```js
document.addEventListener('magewire:init', event => {
    const notification = Magewire.addons.notifier.get(1);
})
```

## `async activate`

Activates a notification.

**Arguments:**

- `id` (number) - Notification ID.

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.activate(1);
})
```

## `async finish`

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

## `async terminate`

Flags a notification as terminated, making it inactive.

**Arguments:**

- `id` (number) - Notification ID.

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.terminate(1);
})
```

## `async fail`

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

## `sync hold`

Clears the active notification timeout.

**Arguments:**

- `id` (number) - Notification ID

**Returns:** `Promise<Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.hold(1);
})
```

## `fetch`

Returns all notifications.

**Returns:** `Array<int, Notification>`

```js
document.addEventListener('magewire:init', event => {
    Magewire.addons.notifier.hold(1);
})
```
