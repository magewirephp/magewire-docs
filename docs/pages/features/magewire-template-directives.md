# Template Directives

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

| Name         | Type  | Area | Description                                | Arguments                    | Since |
|--------------|-------|------|--------------------------------------------|------------------------------|-------|
| `@json`      | -     | Base | Json encodes the given value               | value, default, flags, depth | 3.0.0 |
| `@if`        | Scope | Base | Execute on given condition                 | expression                   | 3.0.0 |
| `@elseif`    | Scope | Base | Execute on given condition, after an `@if` | expression                   | 3.0.0 |
| `@else`      | Scope | Base |                                            | N/A                          | 3.0.0 |
| `@auth`      | Scope | Base |                                            | N/A                          | 3.0.0 |
| `@guest`     | Scope | Base |                                            | N/A                          | 3.0.0 |
| `@foreach`   | Scope | Base |                                            | expression                   | 3.0.0 |
| `@translate` | Scope | Base | Translate a string                         | value, escape                | 3.0.0 |
| `@script`    | Scope | Base | Mark a `<script>` element                  | N/A                          | 3.0.0 |
| `@fragment`  | Scope | Base | Mark a DOM element as a fragment           | type                         | 3.0.0 |

1. Scoped directives always require a corresponding `@end` directive, such as `@if` ... `@endif` or `@auth` ... `@endauth`.
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
    #[\Magewirephp\Magewire\Features\SupportMagewireCompiling\View\Directive\Parser\ScopeDirectiveParser(ExpressionParserType::FUNCTION_ARGUMENTS)]
    public function url(string $url): string
    {
        return "<?= \$escaper->escapeUrl({$url}) ?>";
    }
}
```

As shown in the example, the method is marked with the `FUNCTION_ARGUMENTS` attribute, which indicates that the method
accepts named function arguments that will be automatically passed to it.

| Expression Type      | Description                                              |
|----------------------|----------------------------------------------------------|
| `CONDITION`          | Used for conditional expressions and boolean evaluations |
| `ITERATION_CLAUSE`   | Used for loop constructs and iterative operations        |
| `FUNCTION_ARGUMENTS` | Used for methods that accept named function arguments    |

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

## Actions

Magewire directives are compiled into actual PHP code, which is then placed into real .phtml template files. However, it's important to limit the amount of business logic written directly within these templates.

Ideally, your directive’s compile method should return clean and minimal PHP, such as:

```html
<span>Firstname: <?= $viewModel->renderCustomerFirstname() ?></span>
```

As shown above, this relies on a `$viewModel` object, which must be injected or made available to the template.
While you can provide this ViewModel specifically for that template, it quickly becomes less reusable when others
want to use the same `@` directive elsewhere.

To solve this, Magewire introduces a global variable called `$__magewire`, available only within templates rendered
as part of a Magewire component. This variable acts as a basic ViewModel — referred to as Magewire Underscore.

The `$__magewire` ViewModel provides an `action()` method that accepts a string `$class` argument. This class can either be:

A mapped alias defined in `di.xml`, or

A fully qualified class name that extends the `\Magewirephp\Magewire\Features\SupportMagewireCompiling\View\Management\ActionManager`.

This approach enables your compiled output to remain clean and consistent across templates. For example:

```html
<span>Firstname: <?= $__magewire->action('mapped.namespace')->execute('method_name', ...arguments) ?></span>
```
