# Str

Access under `window.MagewireUtilities.str`. String helpers for UI heuristics.

## `calculateReadingDurationByStrLength(message, options = {})`

Estimate a comfortable auto-dismiss duration for a short message. Returns milliseconds.

```javascript
window.MagewireUtilities.str.calculateReadingDurationByStrLength('Saved.');
// → 3500  (short message → minDuration)

window.MagewireUtilities.str.calculateReadingDurationByStrLength(longMessage);
// → a value between min and max based on length
```

| Option | Default | Meaning |
|---|---|---|
| `minDuration` | `3500` | Floor in ms |
| `maxDuration` | `15000` | Ceiling in ms |
| `baseCharsPerSecond` | `15` | Approximate reading rate |
| `bufferTime` | `1000` | Extra delay added to the estimate |

Typical use: auto-sizing notification duration so long messages stay visible longer without pinning them indefinitely.

## Related

- [JavaScript](../index.md)
- [Notifications](../../../features/notifications.md)
- [Magewire Notifier (addon)](../addons/magewire-notifier.md)
