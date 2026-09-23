# Architecture

Magewire places a PHP component inside Magento's layout and template system.
On an update, the browser sends the component snapshot and requested action;
Magewire reconstructs the layout block, restores state, runs the action, and
renders the PHTML again. The browser then updates the affected DOM.

## Module

The [core repository](https://github.com/magewirephp/magewire) separates
generated Livewire code from Magento integration:

| Path | Responsibility |
|---|---|
| `src/` | Module registration, controllers, observers, configuration, and Magento integration. |
| `lib/` | Magewire mechanisms, features, and adapters. |
| `dist/` | Code ported from Livewire by Portman. Presence here alone does not make a feature active. |
| `portman/` | Overrides used while generating the ported code. |
| `tests/` | Unit and browser coverage for the supported behavior. |

Runtime features are registered by area in
`src/etc/frontend/di.xml` and `src/etc/adminhtml/di.xml`. That registration,
the public `Component` API, and tests are more reliable guides to support
than a class name found in `dist/`.

For the path from a layout block to a component, read
[Layout](layout.md), [Resolvers](mechanisms/resolvers.md), and
[Runtime](runtime.md). When extending the framework, choose a
[Feature](features.md) for component behavior or a
[Mechanism](mechanisms/index.md) for infrastructure. Ordinary application
logic belongs in a Magento service injected into a component.

## Themes

The browser runtime and component actions live in Magewire core. A companion
package adapts loading order, styles, and browser events to a theme or area.
The maintained packages are
[Hyvä Theme](https://github.com/magewirephp/magewire-hyva-theme),
[Hyvä Checkout compatibility](https://github.com/magewirephp/magewire-hyva-checkout),
and [Magento Admin](https://github.com/magewirephp/magewire-admin).

For another theme, follow the
[compatibility-module guide](../../theming/compatibility-module.md).
The component class can remain reusable while the companion module changes
its template and browser bridge.

### Example

The Hyvä package listens for a Magewire flash-message event and hands it to
Hyvä's `dispatchMessages()`. The current integration wraps the inline script
in a CSP-aware fragment:

```php title="Hyvä flash-message bridge"
<?php $script = $block->getData('view_model')->utils()->fragment()->make()->script()->start() ?>
<script>
    window.addEventListener('magewire:flash-messages:dispatch', event => {
        dispatchMessages(Object.values(event.detail));
    });
</script>
<?php $script->end() ?>
```

That bridge belongs to the Hyvä package because `dispatchMessages()` is a
Hyvä API. The component that creates the message does not need to know which
theme displays it. See the
[package source](https://github.com/magewirephp/magewire-hyva-theme/blob/main/src/view/frontend/templates/magewire-features/support-magento-flash-messages/support-magento-flash-messages.phtml)
and [Notifications](../../features/notifications.md) for the component API.
