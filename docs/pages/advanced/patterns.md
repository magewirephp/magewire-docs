# Patterns

!!! warning "While entirely optional, these patterns serve as recommended approaches. They’re open to discussion and improvement—as we’re always learning and evolving to make Magewire better for everyone."

Instead of sharing numerous GitHub Gists, we prefer to share the patterns used within the Magewire core package itself.
These patterns are the result of extensive experimentation and refinement, carefully crafted to keep things clean,
consistent, and maintainable.

## Magewire object on init event

While waiting for Magewire to initialize, you can import any function from the global Magewire object.

```js
document.addEventListener('magewire:init', event => {
    // This shows only a small subset of available options.
    const { addons, utilities, dispatch, on } = event.detail.magewire;
});
```

## AlpineJS Function Proxy

Need to extend or override an AlpineJS component function that's registered with `Alpine.data()`?

This pattern lets you proxy the function regardless of DOM script order.

**Original Component**
```html
<script>
    function magewireNotifier() {
        'use strict';
    
        const notifier = Magewire.addons.notifier;
    
        return {
            terminate: function() {
                notifier.terminate(this.notification.id);
            }
        };
    }
        
    document.addEventListener('alpine:init', () => Alpine.data('magewireNotifier', magewireNotifier), { once: true });
</script>
```

**Proxy Implementation**
```html
<script>
    (function() {
        const original = window.magewireNotifier;

        window.magewireNotifier = function() {
            const result = original();
            const terminate = result.terminate;

            // Extend the terminate method
            result.terminate = function() {
                // You can still access the notification using `this.notification`.
                
                console.log('Custom logic before terminate', this.notification);
                terminate.call(this);
                console.log('Custom logic after terminate');
            };

            return result;
        };
    })();
</script>
```
