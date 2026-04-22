# DOM

Access under `window.MagewireUtilities.dom`.

## `filterDataAttributes(element, prefix = '')`

Extract `data-*` attributes from an element into a keyed object. If a prefix is given, only attributes starting with that prefix are returned, with the prefix stripped from each key. Values that parse as JSON are returned as parsed values; everything else as strings.

```javascript
// <div id="card"
//      data-magewire-title="Hello"
//      data-magewire-count="3"
//      data-other="ignored"></div>

const el   = document.getElementById('card');
const data = window.MagewireUtilities.dom.filterDataAttributes(el, 'magewire');

// → { title: 'Hello', count: 3 }
```

Typical use: hydrate an Alpine component from `data-*` attributes without writing boilerplate.

## Registering your own

`window.MagewireUtilities` is a registry. Add your own pure helpers from an Alpine-init script:

```javascript
document.addEventListener('alpine:init', () => {
    window.MagewireUtilities.register('clipboard', () => ({
        copy(value) { return navigator.clipboard.writeText(value); },
    }));
}, { once: true });
```

Utilities are expected to be **pure functions** — stateless, side-effect-free, predictable. For stateful APIs, use [Addons](../addons/magewire-notifier.md) instead.

## Related

- [JavaScript](../index.md)
- [Str utility](str.md)
- [Loader utility](loader.md)
