# Template Directives

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Magewire compiles component `.phtml` templates before rendering them. The compiler supports Blade-like echo syntax and a focused set of `@` directives while keeping Magento's template variables available.

Compiled views live below `var/magewire/views/{area}/`. They are regenerated when the source changes. Clear them manually after changing compiler configuration or a directive:

```shell
bin/magento magewire:compile:clear
bin/magento magewire:compile:clear --area frontend
```

The compiler has been the `Mechanisms\HandleCompiling` mechanism since Magewire 3.3; the old `Features\SupportMagewireCompiling` namespace no longer exists.

## Echo syntax

{% raw %}
```php
{{ $escaper->escapeHtml($label) }}
{!! $trustedHtml !!}
```
{% endraw %}

{% raw %}`{{ … }}`{% endraw %} escapes output. `{!! … !!}` writes raw output and must only receive trusted HTML.

## Directives

| Syntax | Purpose |
|---|---|
| `@if($condition)` / `@elseif(...)` / `@else` / `@endif` | Conditional output. |
| `@foreach($items as $item)` / `@endforeach` | Iteration. |
| `@auth` / `@endauth` | Render for an authenticated customer. |
| `@guest` / `@endguest` | Render for a guest. |
| `@translate(value: 'Hello', escape: true)` | Translate and optionally escape an expression. |
| `@child('alias')` | Render a child block. |
| `@json(value: $data, flags: 0, depth: 512)` | Encode an expression as JSON. |
| `@escapeUrl($url)` | Escape a URL through Magento's escaper. |
| `@fragment('type')` / `@endfragment` | Wrap output in a typed fragment. |
| `@script` / `@endscript` | Wrap an inline script in the CSP-aware script fragment. |

`@template`, Magewire component/slot directives, and their generated counterparts are compiler internals. Do not call them directly from application templates unless their API becomes explicitly documented.

## Expression arguments

Magewire 3.3 added the `EXPRESSION_ARGUMENTS` parser. It preserves trusted PHP template expressions verbatim and understands named or positional arguments, nested structures, and literal `true`, `false`, and `null` values.

```php
@translate(value: $customer->getFirstname() ?: __('Guest'), escape: true)
@child($showSidebar ? 'sidebar.logged-in' : 'sidebar.guest')
@escapeUrl($block->getUrl('customer/account'))
```

Directives with more than one parameter require named arguments. A single-parameter directive may use a positional argument.

!!! danger "Template source must be trusted"
    Expressions become PHP in the compiled template. Never construct directive source from request data, database content, or other untrusted strings.

## Extending the compiler

Compiler extension classes now live below:

```text
Magewirephp\Magewire\Mechanisms\HandleCompiling\View
```

Important extension points include `Directive`, `DirectiveArea`, `ScopeDirective`, `Management\DirectiveManager`, and the parser types below `Directive\Parser`.

Register a directive in an existing or custom `DirectiveArea` through area-specific `di.xml`. Prefixes map to areas; for example, the `escape` area exposes `@escapeUrl`. Keep compiled output small and delegate business logic to a service or a registered compiler action.

Available parser modes are `CONDITION`, `ITERATION_CLAUSE`, `FUNCTION_ARGUMENTS`, and `EXPRESSION_ARGUMENTS`. Use `EXPRESSION_ARGUMENTS` when arguments must remain valid PHP expressions at render time; use `FUNCTION_ARGUMENTS` only for the older token-style behavior.

See [Handle Compiling](../advanced/architecture/mechanisms/handle-compiling.md) for the mechanism lifecycle.
