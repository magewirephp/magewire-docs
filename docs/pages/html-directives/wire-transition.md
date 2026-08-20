# wire:transition

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-transition") }}

`wire:transition` applies Alpine transitions when Magewire adds or removes an element during DOM morphing:

```php
<button type="button" wire:click="toggleDetails">
    <?= $escaper->escapeHtml(__('Toggle details')) ?>
</button>

<?php if ($magewire->showDetails): ?>
    <div wire:transition>
        <?= $escaper->escapeHtml($magewire->details) ?>
    </div>
<?php endif ?>
```

It also works alongside `wire:show`, where the element stays in the DOM and its visibility changes. Transition
modifiers are Alpine modifiers; make sure the CSS classes or utility styles they rely on are present in the storefront
build.

Use transitions for presentation only. The server-rendered condition remains the source of truth for whether content
exists after a component update.
