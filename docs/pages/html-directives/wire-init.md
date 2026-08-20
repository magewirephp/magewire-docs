# wire:init

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-init") }}

`wire:init` calls an action after the component has initialized in the browser:

```php
<div wire:init="loadRecommendations">
    <?php if ($magewire->ready): ?>
        <!-- Render recommendations. -->
    <?php else: ?>
        <?= $escaper->escapeHtml(__('Loading recommendations…')) ?>
    <?php endif ?>
</div>
```

This creates an additional Magewire request after the initial Magento page response. Use `mount()` for state required
during the first render, and use [lazy loading](../features/lazy-loading.md) when an entire expensive component should be
deferred. `wire:init` is best for optional work that should begin immediately after the page becomes interactive.

Always provide an action expression. In Magewire 3.5, a bare `wire:init` attribute is read as an empty string and does
not reliably fall back to `$refresh`.
