# Patterns

!!! warning "While entirely optional, these patterns serve as recommended approaches. They’re open to discussion and improvement—as we’re always learning and evolving to make Magewire better for everyone."

Instead of sharing numerous GitHub Gists, we prefer to share the patterns used within the Magewire core package itself.
These patterns are the result of extensive experimentation and refinement, carefully crafted to keep things clean,
consistent, and maintainable.

## Alpine Components

New Alpine components created using `.phtml` templates should be stored in files named after the component itself and
placed within the `src/view/{area}/templates/js/alpinejs/components` directory.

```php title="Magewire_Magewirephp::js/alpinejs/magewire-notifier.phtml"
<?= $block->getChildHtml('script-data') ?>
<?= $block->getChildHtml('script-bind') ?>
```

Each component should have its own subfolder named after the component itself, containing at least two files:
`script-data.phtml` and `script-bind.phtml`, which store the component’s data and bindings respectively.

- `/js/alpinejs/components/magewire-notifier/script-data.phtml`
- `/js/alpinejs/components/magewire-notifier/script-bind.phtml` (optional)

Magewire provides a dedicated container specifically for storing any Magewire-related Alpine components.

```xml
<body>
    <referenceContainer name="magewire.alpinejs.components">
        
        <!-- Magewire Notifier - AlpineJS component -->
        <!-- Wrapping block represents the components and is responsible for rendering all parts. -->
        <block name="magewire.alpinejs.components.magewire-notifier"
               template="Magewirephp_Magewire::js/alpinejs/magewire-notifier.phtml"
        >
            <block name="magewire.alpinejs.components.magewire-notifier.script-data"
                   template="Magewirephp_Magewire::js/alpinejs/components/magewire-notifier/script-data.phtml"
                   as="script.data"
            />
            <block name="magewire.alpinejs.components.magewire-notifier.script-bind"
                   template="Magewirephp_Magewire::js/alpinejs/components/magewire-notifier/script-bind.phtml"
                   as="script.bind"
            />
        </block>
    </referenceContainer>
</body>
```

The templates could look like the following:

```html title="js/alpinejs/components/magewire-notifier/script-data.phtml"
<script>
    function magewireNotifier() {
        'use strict';
        
        return {
            create: function() {...},
            update: function() {...},
            delete: function() {...},
        }
    }
    
    document.addEventListener('alpine:init', () => {
        Alpine.data('magewireNotifier', magewireNotifier);
    }, { once: true })
</script>
```

!!! info "By assigning components through a function, you gain flexibility to adjust or proxy the logic elsewhere—outside the template file. This approach keeps your templates clean and makes it easier to maintain or override behavior without directly modifying the view."

And:

```html title="js/alpinejs/components/magewire-notifier/script-bind.phtml"
<script>
    function magewireNotifierBindings() {
        'use strict';
        
        return {
            
            <!-- Binds the "magewire-notifications" class to the root element of the component. -->
            'x-bind:class'() {
                return 'magewire-notifications';
            }
        };
    }

    document.addEventListener('alpine:init', () => {
        Alpine.bind('magewireNotifierBindings', magewireNotifierBindings);
    }, { once: true })
</script>
```

!!! info "By assigning bindings through a function, you gain flexibility to adjust or proxy the logic elsewhere—outside the template file. This approach keeps your templates clean and makes it easier to maintain or override behavior without directly modifying the view."

Finally, these can be used within your UI component:

```html title="magewire/ui-components/notifier.phtml"
<div x-data="magewireNotifier" x-bind="magewireNotifierBindings">
    
</div>
```

Sub-elements within a component can also have their own bindings by using the bindings object, which each component is
typically expected to provide. This object contains named sub-objects for specific purposes.

For example, a wrapping `<div>` for a notification list item might require a binding like `x-bind="bindings.notification.wrapper"`.

```html title="js/alpinejs/components/magewire-notifier/script-data.phtml"
<script>
    function magewireNotifier() {
        'use strict';
        
        return {
            create: function() {...},
            update: function() {...},
            delete: function() {...},
            
            bindings: {
                notification: {
                    wrapper: function () {
                        return {
                            'x-bind:class='() {
                                return {
                                    'notification'
                                }
                            },
                            
                            'x-on:click'() {
                                this.terminate()
                            }
                        }
                    }
                }
            }
        }
    }
    
    document.addEventListener('alpine:init', () => {
        Alpine.data('magewireNotifier', magewireNotifier);
    }, { once: true })
</script>
```

Nested elements can leverage this structure as shown below:

```html title="magewire/ui-components/notifier.phtml"
<div x-data="magewireNotifier" x-bind="magewireNotifierBindings">
    <template x-for="...">
        <div x-show="notification.active" x-bind="bindings.notification.wrapper">
            <div x-text="notification.title" x-bind="bindings.notification.title">
                
            </div>
        </div>
    </template>
</div>
```

!!! warning "Bindings defined in a `script-bind.phtml` file using `Alpine.bind()` behave differently from the example above, where bindings are applied directly to a specific Alpine component. Ultimately, all bindings are optional — this method simply offers a reusable way to avoid manually managing required DOM element attributes."

### CSP compatibility

Magewire is designed to be fully CSP-compliant. This means it no longer supports method calls with arguments directly in the DOM,
such as `create('Foo', true)` within attributes like `x-on:click`. While this limitation can seem restrictive—especially
when you have methods that normally expect arguments—it’s a necessary trade-off to maintain security.

In CSP-restricted environments, the only way to pass dynamic data into such methods is typically through `data-` attributes,
accessible from within an Alpine component via `this.$el`. However, relying solely on this approach tightly couples your
logic to the DOM structure and Alpine components. As a result, methods like create cannot be used outside of an Alpine
context or without the presence of specific DOM attributes.

To address this, Magewire adopts a pattern that preserves flexibility: functionality is written in a way that resembles an API.
This allows you to invoke methods like `create` from different contexts—such as the browser console or other JavaScript logic—without depending on the DOM.

Alongside this API, each component also exposes a `csp` object. This object provides a CSP-safe interface where methods never accept arguments.
These methods are purpose-built for use in contexts like `x-on:click` and ensure compatibility with strict CSP settings.

Let’s look at an example to clarify this pattern:

```html title="js/alpinejs/magewire/addons/notifier.phtml"
<script>
    
    // API.
    function magewireNotifierAddon() {
        'use strict';

        return {
            notifications: [],

            create: function(notification) {
                this.notifications.push(notification)
            },

            // CSP version.
            csp: function() {
                const origin = this

                return {
                    // Optional: depends on the API methods.
                    ...origin,

                    create: function () {
                        origin.create({ text: this.$el.dataset('create-text')})
                    }
                }
            }
        }
    }
    
    document.addEventListener('magewire:init', () => Magewire.addon('notifier', magewireNotifierAddon, true), { once: true });
</script>
```

This enables you to call Magewire.addon.notifier.create({ text: 'Foo' }) wherever method arguments are allowed,
like in your own JavaScript code outside of CSP-restricted contexts.

When using the same notifications inside an Alpine component (CSP-safe), it would look like this:

```html title="js/alpinejs/components/magewire-notifier/script-data.phtml"
<script>
    
    // Alpine component
    function magewireNotifier() {
        'use strict';

        return {
            // Spread the CSP-safe version of the notifier API for use within an Alpine component.
            ...Magewire.addons.notifier.csp(),

            // Global state reactive notifications.
            get notifications() {
                return Magewire.addons.notifier.notifications;
            },
        }
    }
</script>
```

!!! danger "It might seem like overkill to some — and that’s fine. We value reusability, even if something ends up being used only once. This pattern keeps things clean and well-structured."
