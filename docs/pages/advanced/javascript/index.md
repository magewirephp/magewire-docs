# JavaScript

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/javascript") }}

Magewire exposes the ported Livewire runtime as `window.Magewire` and adds two registries:

- `window.MagewireAddons` for stateful, feature-level browser APIs;
- `window.MagewireUtilities` for reusable helper functions.

These registries are `Map`-like objects. Registered values are also available as properties, such as `window.MagewireAddons.notifier`.

## Initialization

Use the globals directly; `event.detail.magewire` is not part of Magewire's
initialization event. Place registrations in a PHTML block under the
appropriate [layout node](../../theming/layout-containers.md) and use a
CSP-aware Script fragment:

```php title="view/frontend/templates/js/magewire/commit-listener.phtml"
<?php $script = $block->getData('view_model')->utils()->fragment()->make()->script()->start() ?>
<script>
    document.addEventListener('magewire:init', () => {
        window.Magewire.hook('commit', ({ component, commit, succeed }) => {
            succeed(({ snapshot, effects }) => {
                // React after a successful commit.
            })
        })
    }, { once: true })
</script>
<?php $script->end() ?>
```

The Hyvä companion package forwards the corresponding `livewire:init` and `livewire:initialized` events to the Magewire names for compatibility. Application integrations should use the Magewire names.

## Register an addon

Place the registration template below the `magewire.addons.after` container
so built-in addons register first, then call `register()`:

```xml title="view/frontend/layout/default.xml"
<referenceContainer name="magewire.addons.after">
    <block name="vendor.magewire.addons.cart-preview"
           template="Vendor_Module::js/magewire/addons/cart-preview.phtml" />
</referenceContainer>
```

```php title="view/frontend/templates/js/magewire/addons/cart-preview.phtml"
<?php $script = $block->getData('view_model')->utils()->fragment()->make()->script()->start() ?>
<script>
    function cartPreviewAddon() {
        return {
            open: false,
            toggle() { this.open = !this.open }
        }
    }

    window.MagewireAddons.register('cartPreview', cartPreviewAddon, true)
</script>
<?php $script->end() ?>
```

The third argument makes the returned object Alpine-reactive. Registration is queued until Alpine exists when necessary. If the registered value defines `init()`, the registry invokes it once.

## Register a utility

Add a template below `magewire.utilities.after` and use the equivalent
registry. Inside its Script fragment:

```javascript
function currencyUtility() {
    return {
        format(value) {
            return new Intl.NumberFormat().format(value)
        }
    }
}

window.MagewireUtilities.register('currency', currencyUtility)
```

Access it as `window.MagewireUtilities.currency`. Built-in utilities are `cookie`, `dom`, `loader`, and `str`.

## Feature scripts

Feature bridges are normally injected below the `magewire.features` layout node and can register standard `Magewire.hook()` callbacks. Keep theme rendering in a theme package and browser behavior in the feature that owns it.
