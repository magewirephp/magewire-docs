# wire:show

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-show") }}

`wire:show` toggles an element's visibility from a component property without removing the element from the DOM:

```php
<button type="button" wire:click="toggleFilters">
    <?= $escaper->escapeHtml(__('Toggle filters')) ?>
</button>

<div wire:show="filtersOpen">
    <?= $block->getChildHtml('filters') ?>
</div>
```

Magewire maps the directive to Alpine's `x-show`, so visibility changes as soon as browser-side component state
changes. Prefix the expression with `!` to invert it and combine it with `wire:transition` when the change should be
animated.

Hidden content remains in the DOM. Use a PHP conditional when the server must omit sensitive or expensive markup
entirely; CSS visibility is never an authorization boundary.
