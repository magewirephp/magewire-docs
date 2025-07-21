# Flakes

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Flakes are reusable UI components that provide a powerful way to create modular, composable elements within your applications.
Think of them as self-contained building blocks that can be embedded anywhere within your Magewire components using familiar HTML-like syntax.

What makes flakes particularly useful is their flexibility and ease of use. They allow you to encapsulate complex
UI logic, styling, and behavior into reusable components that can be shared across different parts of your application.
Whether you're building alert messages, form inputs, modal dialogs, or any other UI element, flakes provide a clean and
consistent approach to component composition.

## Example

Flakes use an `magewire:` prefix (similar to Alpine.js or Vue.js custom elements) combined with `mw:` and `:` prefixed attributes to
bind Magewire-specific data and pass parameters to the component during mounting. This syntax makes them intuitive to
use while maintaining the full power of Magewire's reactive capabilities.

```html title="view/{area}/templates/magewire/foo.phtml"
<div>
    Foo!
    
    <magewire:message mw:name="custom-alert" :type="error">
        This is an error message!
    </magewire:message>
</div>
```

### Registration

To use flakes, you must first register them in the `magewire_flakes.xml` layout handle:

```xml title="view/{area}/layout/magewire_flakes.xml"
<body>
    <block name="flakes.message"
           as="message"
           template="Magewirephp_Magewire::magewire/flakes/message.phtml"
    >
        <arguments>
            <argument name="magewire" xsi:type="object" shared="false">
                Magewirephp\Magewire\Magewire\Flake\Message
            </argument>
        </arguments>
    </block>
</body>
```

### Component Class

Attributes prefixed with `:` are automatically passed to the component's `mount()` method:

```php title="Vendor\Module\Magewire\Flake\Message"
<?php

class Message extends \Magewirephp\Magewire\Component
{
    public string $type = 'error';

    public function mount(string $type = 'info')
    {
        $this->type = $type;
    }
}
```

### Template

Finally, create the flake template:

```html title="view/{area}/templates/magewire/flakes/message.phtml"
<div role="alert" class="message <?= $magewire->type ?>">
    ...
</div>
```
