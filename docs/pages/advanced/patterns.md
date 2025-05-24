# Patterns

!!! warning "While entirely optional, these patterns serve as recommended approaches. They’re open to discussion and improvement—as we’re always learning and evolving to make Magewire better for everyone."

Instead of sharing numerous GitHub Gists, we prefer to share the patterns used within the Magewire core package itself.
These patterns are the result of extensive experimentation and refinement, carefully crafted to keep things clean,
consistent, and maintainable.

## Alpine Components

New Alpine components created using `.phtml` templates should be stored in files named after the component itself and
placed within the `src/view/{area}/templates/js/alpinejs` directory.

```php title="Magewire_Magewirephp::js/alpinejs/magewire-notifier.phtml"
<?= $block->getChildHtml('script-data') ?>
<?= $block->getChildHtml('script-bind') ?>
```

Each component should have its own subfolder named after the component itself, containing at least two files:
`script-data.phtml` and `script-bind.phtml`, which store the component’s data and bindings respectively.

- `/js/alpinejs/magewire-notifier/script-data.phtml`
- `/js/alpinejs/magewire-notifier/script-bind.phtml` (optional)

Magewire provides a dedicated container specifically for storing any Magewire-related Alpine components.

```xml
<body>
    <referenceContainer name="magewire.alpinejs.components">
        
        <!-- Magewire Notifier - AlpineJS component -->
        <block name="magewire.alpinejs.components.magewire-notifier"
               template="Magewirephp_Magewire::js/alpinejs/magewire-notifier.phtml"
        >
            <block name="magewire.alpinejs.components.magewire-notifier.script-data"
                   template="Magewirephp_Magewire::js/alpinejs/magewire-notifier/script-data.phtml"
                   as="script.data"
            />
            <block name="magewire.alpinejs.components.magewire-notifier.script-bind"
                   template="Magewirephp_Magewire::js/alpinejs/magewire-notifier/script-bind.phtml"
                   as="script.bind"
            />
        </block>
    </referenceContainer>
</body>
```

The templates could look like the following:

```html title="js/alpinejs/magewire-notifier/script-data.phtml"
<script>
    function magewireNotifier() {
        return {
            create() {...},
            update() {...},
            delete() {...},
        }
    }
    
    document.addEventListener('alpine:init', () => {
        Alpine.data('magewireNotifier', magewireNotifier);
    }, { once: true })
</script>
```

!!! info "By assigning components through a function, you gain flexibility to adjust or proxy the logic elsewhere—outside the template file. This approach keeps your templates clean and makes it easier to maintain or override behavior without directly modifying the view."

And:

```html title="js/alpinejs/magewire-notifier/script-bind.phtml"
<script>
    function magewireNotifierBindings() {
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
