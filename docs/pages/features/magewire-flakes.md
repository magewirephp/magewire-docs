# Flakes

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Flakes are reusable UI components that provide a powerful way to create modular, composable elements within your applications.
Think of them as self-contained building blocks that can be embedded anywhere within your Magewire components using familiar HTML-like syntax.

What makes flakes particularly useful is their flexibility and ease of use. They allow you to encapsulate complex
UI logic, styling, and behavior into reusable components that can be shared across different parts of your application.
Whether you're building alert messages, form inputs, modal dialogs, or any other UI element, flakes provide a clean and
consistent approach to component composition.

## Example

Flakes use the `magewire:` prefix (similar to custom elements in Alpine.js or Vue.js) combined with special attributes to
bind Magewire-specific data and pass parameters to the component during mounting. You can also bind property values
directly using the `prop:` prefix followed by the property name. This syntax keeps usage intuitive while preserving the
full power of Magewire’s reactive capabilities.

```html title="view/{area}/templates/magewire/foo.phtml"
<div>
    Foo!
    
    <?php $title = 'Hello World' ?>
    <magewire:message name="custom-alert" prop:type="error" mount:title="$title" />
</div>
```

As you can see, any variables defined within the template will automatically be bound as arguments to either a `mount` method
or can be used as component public property values.

Let's imagine you need the escaper within the `mount` method that sits within your Magewire component.
You could inject it via the `__construct` method, but since it already exists within the template, you can do the following:

```html title="view/{area}/templates/magewire/foo.phtml"
<div>
    <magewire:message name="custom-alert" mount:escaper="$escaper" prop:view-model="$block" />
</div>
```

_Since `$escaper` is a global variable, you don't need to define it explicitly._

The component might look something like this:

```php title="Vendor\Module\Magewire\Flake\Message"
<?php

class Message extends \Magewirephp\Magewire\Component
{
    public function mount(\Magento\Framework\Escaper $escaper)
    {
        $this->title = $title;
    }
}
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

Attributes prefixed with `mount:` are automatically passed to the component’s `mount()` method. Template variables can be
defined directly using the `$foo` syntax. This makes passing full objects from your template to your Magewire component easier than ever.

```php title="Vendor\Module\Magewire\Flake\Message"
<?php

class Message extends \Magewirephp\Magewire\Component
{
    public string $type = 'error';
    public string $title = 'No Title';

    public function mount(string $title)
    {
        $this->title = $title;
    }
}
```

### Template

Finally, create the flake template:

```html title="view/{area}/templates/magewire/flakes/message.phtml"
<div role="alert" class="message <?= $magewire->type ?>">
    <div class="title text-lg">
        <?= $magewire->title ?>
    </div>
</div>
```
