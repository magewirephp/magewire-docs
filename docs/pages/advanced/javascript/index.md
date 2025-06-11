# JavaScript

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/javascript") }}

## Utilities

!!! info "View all available utilities [here](utilities.md)."

In addition to the core library, Magewire provides a `utilities` object as a centralized place to store custom support
functionality that can be useful throughout the framework — such as splitting strings, validating objects,
extracting attributes from DOM elements, and more.

These utilities serve as general-purpose helpers, whereas addons are more specialized and should be thought of as APIs.

You can register a utility like this:

```xml title="view/frontend/layout/default.xml"
<referenceContainer name="magewire.utilities">
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

!!! info "View all available addons [here](addons.md)."

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
                }
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
