# Themes

Magewire is Hyvä-compatible out of the box, meaning we actively design features to work seamlessly with the Hyvä theme.
However, it’s absolutely possible to integrate Magewire with other themes as well.

While this may require more effort, Magewire’s event-driven architecture and minimalist file structure make it flexible.
Many components can be moved, extended, or overridden as needed to support different frontends.

## Supported Themes

| Theme         | Parent     |
|---------------|------------|
| Hyvä Theme    | Hyvä Reset |
| Magento Admin | -          |

## Compatibility

Making a theme compatible with Magewire requires a solid understanding of Magewire’s frontend architecture,
including its folder and file structure, dispatched events, available features, addons, and custom directives.

Additionally, Magewire relies heavily on AlpineJS as its core frontend engine. If your theme already includes AlpineJS,
you’ll need to either remove your version in favor of the one bundled with Magewire or disable it on pages where
Magewire is used to avoid conflicts.

Below is an example of how dispatched flash messages from a component can be made compatible:

```php title="src/Magewire/Example.php"
<?php

namespace Example\Module\Magewire\Example;

class Example extends \Magewirephp\Magewire\Component
{
    public function click(): void
    {
        $this->dispatchSuccessMessage(__('Hello World'))
    }
}
```

By default, there is no frontend event listener for the `magewire:flash-messages:dispatch` event. To make this work,
a compatibility layer needs to be added.

In the case of the Hyvä Theme, the following approach can be used:

```xml
<body>
    <referenceContainer name="magewire.features">
        <block name="magewire.features.support-magento-flash-messages"
               template="Magewirephp_MagewireCompatibilityWithHyva::js/magewire/features/support-magento-flash-messages/support-magento-flash-messages.phtml"
        />
    </referenceContainer>
</body>
```

Here’s the template content used to achieve this:

```html
<script>
    (() => {
        window.addEventListener('magewire:flash-messages:dispatch', event => dispatchMessages(event.detail));
    })();
</script>
```

The `magewire:flash-messages:dispatch` event includes the following data:

```json
{
    "detail": {
        "0": {
            "text": "Hello World",
            "type": "success"
        }
    }
}
```
