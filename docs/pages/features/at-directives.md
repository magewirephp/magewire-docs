# Directives

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Starting from Magewire V3, all templates are precompiled into the generated directory, but only when no existing compilation
is found or when the source template has been modified. This pre-compilation is powered by the new Compiling feature,
which is now a core part of the framework.

Thanks to this feature, simplified `@`-directives can be used in templates and are automatically compiled into real PHP code.
For example, there's no longer a need to include view models just to check session-related logic—such as determining if
a customer is a guest or logged in. Instead, you can now simply wrap your logic in `@auth` and `@endauth` directives,
with any necessary code in between.

What's more, the system is designed to be extensible. Developers can easily inject their own custom directives,
making the development experience more streamlined and efficient.

**Example**

```html
<div>
    @auth
        <!-- Will only be shown to logged in customers. -->
        <span>Hi customer</span>
    @endauth
    
    @guest
        <!-- Will only be shown to guests. -->
        <span>Hi guest</span>
    @endguest
    
    @json(value: '{"firstname": "John", "lastname": "Doe"}')
</div>
```

## Directives

| Name    | Type  | Area | Description                  | Arguments                    | Since |
|---------|-------|------|------------------------------|------------------------------|-------|
| `@json` | -     | Base | Json encodes the given value | value, default, flags, depth | 3.0.0 |
| `@if`   | Scope | Base | Execute on given condition   | expression                   | 3.0.0 |

1. Scoped directives always require a corresponding `@end` directive, such as `@if` ... `@endif`.
2. Named arguments are used by default, allowing you to pass arguments in any order.
3. Areas can be custom-defined and act as directive prefixes. For example, the directive escapeHtml belongs to the escape area, indicating it was registered within that namespace.

## Customize

Got an idea for a custom directive? Go ahead and build it using a bit of dependency injection, the Directive Manager,
and our abstraction layer to help you get started.

Useful classes to discover are:

**...\Features\SupportMagewireCompiling\View\Management**

- DirectiveManager

**...\Features\SupportMagewireCompiling\View**

- Directive *(abstract)*
- DirectiveArea *(abstract)*
- ScopeDirective *(abstract)*
- Compiler *(abstract)*

**...\Features\SupportMagewireCompiling\View\Directive**

- Scope

**...\Features\SupportMagewireCompiling\View\Compiler**

- MagewireCompiler

**..\Features\SupportMagewireCompiling\View\Directive\Parser**

- FunctionArgumentsParser

**..\Support**

- Parser *(abstract)*

### Areas

Areas serve as prefixes for your directives. When you use a directive like `@fooBar`, the compiler interprets `foo` as the
area and checks if it exists. If it does, it will then invoke the `bar` directive within that area.

```xml title="File: etc/frontend/di.xml"
<virtualType name="Example\Module\Magewire\Features\SupportFooDirective\View\FooDirectiveArea"
             type="Magewirephp\Magewire\Features\SupportMagewireCompiling\View\DirectiveArea"
>
    <arguments>
        <argument name="directives" xsi:type="array">
            
            <!--
                Inject the "bar" directive into the area.
            -->
            <item name="bar" xsi:type="object">
                Example\Module\Magewire\Features\SupportFooDirective\View\Directive\Bar
            </item>
        </argument>
    </arguments>
</virtualType>

<type name="Magewirephp\Magewire\Features\SupportMagewireCompiling\View\Management\DirectiveManager">
    <arguments>
        <argument name="areas" xsi:type="array">
            
            <!--
                Inform the Directive Manager about the "foo" area.
            -->
            <item name="foo" xsi:type="object">
                Example\Module\Magewire\Features\SupportFooDirective\View\FooDirectiveArea
            </item>
        </argument>
    </arguments>
</type>
```

### Directives

There are multiple ways to create a directive. In most cases, the abstraction layer handles the heavy lifting,
but you can opt for a more customized approach when the situation requires it.

Below are two examples, each demonstrating a different use case that required a unique approach.

**Example for: `@escapeUrl(url: 'https://example.test')`**

In this example, the directive class was injected into the **escape** area, where the `url` method corresponds to the directive suffix `Url`.

```php title="Class: ...\Features\SupportMagewireCompiling\View\Directive\Magento\Escape"
<?php

class Escape extends \Magewirephp\Magewire\Features\SupportMagewireCompiling\View\Directive
{
    public function url(string $url): string
    {
        return "<?= \$escaper->escapeUrl({$url}) ?>";
    }
}
```

**Example for: `@json(value: ['foo' => 'bar'])`**

A directive injected into the **Base** area, allowing it to be used directly without a prefix.

```php title="Class: ...\Features\SupportMagewireCompiling\View\Directive\Json"
<?php

class Escape extends \Magewirephp\Magewire\Features\SupportMagewireCompiling\View\Directive
{
    private int $encodingOptions = JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_AMP | JSON_HEX_QUOT;

    public function compile(string $expression, string $directive): string
    {
        $arguments = $this->functionArgumentsParser()->parse($expression)->arguments();

        $value = $arguments->get('value', $arguments->get('default', []));
        $flags = $arguments->get('flags', $this->encodingOptions);
        $depth = $arguments->get('depth', 512);

        return "<?php echo json_encode($value, $flags, $depth) ?>";
    }
}
```

Both examples extend from the base Directive class. The first relies on the abstraction's compile method,
which automatically looks for a corresponding method with a matching name.

The second handles compilation manually, since it only requires a single method.

While this could have been solved by defining a public `json` method, in this case, it was necessary to manually handle
`$encodingOptions` to apply default flags when none are provided by the developer.

## Roadmap

{{ include("admonition/roadmap.md") }}

| Subject               | Description                                                                                                                               |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Precompilers          | Precompile specific template context into `@` prefixed directives.                                                                        |
| Component Precompiler | Converts `<x-component name="foo">` tags into `@magewireComponent(name: 'foo')` directives automatically during the precompilation phase. |

