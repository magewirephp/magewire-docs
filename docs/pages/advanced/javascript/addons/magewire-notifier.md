# Magewire Notifier

The notifier is available as `window.MagewireAddons.notifier` after Magewire's layout resources have registered.

```javascript
document.addEventListener('magewire:init', async () => {
    const notification = await window.MagewireAddons.notifier.create(
        'Task completed.',
        { type: 'success', duration: 5000, activate: true },
        {
            onActivate: ({ notification }) => console.log(notification.id),
            onClick: ({ event, preventDefault }) => {},
        },
    )
}, { once: true })
```

## Creating notifications

`create(message, options = {}, hooks = {})` returns `Promise<Notification>`.

Options include:

- `type`: `success`, `error`, `warning`, or `info`;
- `title`: optional title;
- `duration`: display duration in milliseconds;
- `recoverable`: marks the item as recoverable;
- `activate`: activate immediately, defaulting to `true`.

When `duration` is `null`, Magewire calculates a reading duration from the message length. Values `0` and `false` currently become 24 hours; they are not permanently sticky.

## Repeated messages

Since Magewire 3.6, the notifier coalesces an immediately repeated message when all of the following
are true:

- the previous notification is still active;
- its message and type match the new notification;
- the new call uses `activate: true`.

Instead of appending another item, `create()` returns the existing notification with the same `id`,
increments its `occurrences`, merges any new hooks, and restarts its cleanup timer. Different text,
a different type, an inactive previous notification, or `activate: false` creates a separate item.

The built-in presentation shows an occurrence badge after the count reaches two. Integrations can
read `notification.occurrences` and style or announce repeated messages differently.

Per-notification hook names are:

- `onCreate`
- `onUpdate`
- `onActivate`
- `onCleanup`
- `onTerminate`
- `onRecover`
- `onStateChange`
- `onClick`
- `onFailure`

Hooks receive an object. For example, `onStateChange` receives `{ state, previous, notification }` and `onFailure` receives `{ notification, reason }`.

## Methods

| Method | Result |
|---|---|
| `get(id)` | Return a notification or `null`. |
| `update(id, changes = {}, hooks = {})` | Hold and update an existing notification, merge hooks, and restart cleanup while active. |
| `activate(id)` | Activate, finish, and schedule cleanup. |
| `finish(id)` | Mark the notification successful. |
| `terminate(id)` | Hold and terminate it. |
| `fail(id, reason = null)` | Mark it failed. |
| `cleanup(id)` | Schedule it to become inactive after its duration. |
| `hold(id)` | Clear its active timeout. |
| `recover(id)` | Hold it, run recovery hooks, and mark it recovered. |
| `trigger(hook, args = {}, notification = null)` | Run item and global hooks. |

There is no `fetch()` method. Read the reactive `notifications` array when a UI needs the complete collection.

## Global hooks

The notifier also triggers Magewire hooks:

```javascript
window.Magewire.hook(
    'addons.notifier.state-change',
    ({ state, previous, notification }) => {},
)
```

Available suffixes are `create`, `update`, `activate`, `cleanup`, `terminate`, `recover`, `state-change`, and `failure`.
