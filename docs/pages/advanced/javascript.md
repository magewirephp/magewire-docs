# JavaScript

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/javascript") }}

## Utilities

In addition to the core library, Magewire provides a `utilities` object as a centralized place to store custom support
functionality that can be useful throughout the framework — such as splitting strings, validating objects,
extracting attributes from DOM elements, and more.

These utilities serve as general-purpose helpers, whereas addons are more specialized and should be thought of as APIs.

You can register a utility like this:

```xml title="view/frontend/layout/default.xml"
<referenceContainer name="magewire.addons">
    <block name="magewire.utilities.notifier"
           template="Example_Module::view/frontend/templates/js/magewire/utils/dom.phtml"
    />
</referenceContainer>
```

And you can define the utility itself using the following code:

```html
<script>
    function magewireDomUtility() {
        'use strict';

        return {
            filterDataAttributes: function (element, prefix = '') {
                return {};
            }
        }
    }
    
    document.addEventListener('magewire:init', () => Magewire.utility('dom', magewireDomUtility));
</script>
```

!!! warning "Magewire utilities are stored in the `/utils` directory, rather than in a folder named `/utilities`."

## Addons

In addition to the core library, Magewire provides an `addons` object as a centralized place to store custom
functionality—avoiding the need to attach them to the global (and often cluttered) `window` object.

You can register an addon like this:

```xml title="view/frontend/layout/default.xml"
<referenceContainer name="magewire.addons">
    <block name="magewire.addons.notifier"
           template="Example_Module::view/frontend/templates/js/magewire/addons/notifier.phtml"
    />
</referenceContainer>
```

And define the addon itself with the following code:

```html
<script>
    function magewireNotifierAddon() {
        'use strict';

        return {
            notifications: [],

            create(text) {
                this.notifications.push({text: text});
            }
        }
    }

    document.addEventListener('magewire:init', () => Magewire.addon('notifier', magewireNotifierAddon, true), { once: true });
</script>
```

!!! tip "Reactivity"
    The third argument, `reactive`, allows developers to make the addon reactive using `Alpine.reactive()`.
    This is useful if you want to expose your addon as an Alpine component with a globally accessible `notifications` array,
    while still being able to leverage features like `this.$watch('notifications', (current, previous) => {})` change tracking.

## Alpine components

To make your addon available as an Alpine component where `notifications` are globally accessible, you’ll want to ensure
that other Alpine components can inject `notifications` into it—without introducing conflicts or requiring multiple,
isolated notifications arrays in the DOM.

You can register your AlpineJS component like this:

```xml title="view/frontend/layout/default.xml"
<referenceContainer name="magewire.alpinejs.components">
    <block name="magewire.alpinejs.components.magewire-notifier"
           template="Example_Module::js/alpinejs/magewire-notifier.phtml"
    />
</referenceContainer>
```

And then define the corresponding Alpine component as follows:

```html
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('magewireNotifier', () => ({
            ...Magewire.addons.notifier, ...{
                get notifications() {
                    return Magewire.addons.notifier.notifications;
                },
            }
        }));
    });
</script>
```

In this case, we create a getter for the `notifications`, allowing us to expose the notifier’s internal notification array
in a way that's usable in your HTML—such as with `<template x-for="notification in notifications">`.

??? warning "Caveats When Sharing Objects Between `Alpine.store()` and `Alpine.data()`"
    AlpineJS allows you to define global state using `Alpine.store()` or `this.$store()`, depending on context.
    Objects stored this way are automatically made reactive via `Alpine.reactive()` under the hood.

    However, there's a caveat: if the stored object includes an `init` method, Alpine will automatically invoke it upon storing.
    
    Later, if you use that same object in a component via `Alpine.data()`, the init method will be triggered again,
    since `Alpine.data()` also auto-invokes init. This behavior can lead to unintended side effects, requiring you to be
    cautious—if the object has an `init` method, you may need to override it with an empty function to avoid double execution.

### CSP-compliant

Magewire is CSP-compliant out of the box, and we strongly encourage you to follow the same approach when developing additional components.
Using the previous example, you can easily adapt a non-compliant component into a CSP-compliant one with minimal changes.

```html
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('magewireNotifier', () => ({
            ...Magewire.addons.notifier.csp(),
            
            get notifications() {
                return Magewire.addons.notifier.notifications;
            }
        }));
    });
</script>
```

As you may notice, the change involves switching from `...Magewire.addons.notifier` to `...Magewire.addons.notifier.csp()`.
This returns a CSP-compliant version in which methods no longer accept arguments.

Here's what that might look like in practice:

```html
<script>
    document.addEventListener('magewire:init', () => {
        Magewire.addon('notifier', () => ({
            notifications: [],

            create(text) {
                this.notifications.push({ text: text });
            },

            csp() {
                const origin = this

                return {
                    ...origin, ...{
                        create() {
                            this.notifications.push({ text: this.$el.dataset.text })
                        }
                    }
                }
            }
        }), true);
    });
</script>
```

At first glance, this approach may seem overly complex—and that’s a fair impression. However, it’s intentional.

By structuring it this way, the Magewire addon can be reused elsewhere in your JavaScript, where you can pass arguments
directly to methods without relying on an HTML element with a dataset. The csp method, however, is designed exclusively
for use within Alpine components. This guarantees that `this.$el` is always available and behaves consistently,
without risk of breaking functionality.
