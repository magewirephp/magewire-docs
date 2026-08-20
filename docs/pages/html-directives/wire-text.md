# wire:text

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-text") }}

`wire:text` writes a component property into an element's text content:

```html
<output wire:text="formattedTotal"></output>
```

Magewire maps this directive to Alpine's `x-text`. Because it writes text rather than HTML, markup in the value is not
interpreted by the browser. Prefix the expression with `!` for a boolean inverse, or use a normal escaped PHP expression
when the value only needs to change after a server render.

Use a translated, server-formatted public property for customer-facing currency, dates, and labels. Do not move Magento
formatting rules into the directive expression.
