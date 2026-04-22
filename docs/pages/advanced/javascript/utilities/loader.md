# Loader

Access under `window.MagewireUtilities.loader`. Helpers for parsing loader-message text into structured parts — used by `wire:loading` text interpolation and the notifier.

## `parseText(text)`

Parse a loader message into an ordered list of `{ text, title? }` parts.

The parser recognises three shapes:

| Shape | Input | Output |
|---|---|---|
| Simple | `"Saving"` | `[{ text: 'Saving' }]` |
| Titled | `"Save: In progress"` | `[{ title: 'Save', text: 'In progress' }]` |
| Separated | `"Saving ... Almost done"` | `[{ text: 'Saving' }, { text: 'Almost done' }]` |
| Continuation | `"...Almost done"` | `[{ text: null }, { text: 'Almost done' }]` |

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
