# Loader

Access under `window.MagewireUtilities.loader`. Helpers parse Magewire's component `$loader` message text into
structured parts used by the Magewire loader Feature and notifier. The standard `wire:loading` directive controls
element state; it does not use this utility for text interpolation.

## `parseText(text)`

Parse a loader message into an ordered list of `{ text, title? }` parts.

The parser recognises four shapes:

| Shape | Input | Output |
|---|---|---|
| Simple | `"Saving"` | `[{ text: 'Saving' }]` |
| Titled | `"Save: In progress"` | `[{ title: 'Save', text: 'In progress' }]` |
| Separated | `"Saving ... Almost done"` | `[{ text: 'Saving' }, { text: 'Almost done' }]` |
| Continuation | `"...Almost done"` | `[{ text: null }, { text: 'Almost done' }]` |

A message is separated only when it contains three periods with a space on both sides, or starts with three periods.
`"Hi... there"` stays a single part.

```javascript
const parts = window.MagewireUtilities.loader.parseText('Save: In progress ... Done');
// [
//   { title: 'Save', text: 'In progress' },
//   { text: 'Done' },
// ]
```

## Related

- [JavaScript](../index.md)
- [wire:loading](../../../html-directives/wire-loading.md)
- [Magewire Loaders](../features/magewire-loaders.md)
