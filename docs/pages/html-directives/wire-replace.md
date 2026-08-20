# wire:replace

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-replace") }}

`wire:replace` tells Magewire to replace an element's children instead of morphing them individually:

```php
<div wire:replace>
    <?= $block->getChildHtml('third-party-widget') ?>
</div>
```

Use it when preserving intermediate DOM nodes would leave a widget or browser-managed subtree in an invalid state.
The `.self` modifier replaces the element itself rather than only its contents.

Replacement discards browser state, focus, event listeners, and third-party instances below the replaced boundary.
Prefer normal morphing for forms and interactive controls unless complete replacement is intentional; use
[`wire:ignore`](wire-ignore.md) when the browser widget, rather than the server render, should retain ownership.
