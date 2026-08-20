# wire:loading

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-loading") }}

`wire:loading` toggles an element for the duration of a component commit. Magewire's base CSS hides loading elements
before the browser runtime starts, preventing an initial flash.

```php
<button type="button" wire:click="save" wire:loading.attr="disabled">
    <?= $escaper->escapeHtml(__('Save')) ?>
</button>

<span wire:loading.delay wire:target="save" role="status">
    <?= $escaper->escapeHtml(__('Saving…')) ?>
</span>
```

Use `wire:target` to limit the state to a specific action or property update. Without a target, the element responds to
compatible commits from its component. Delay modifiers avoid flashing an indicator for fast requests; display, class,
attribute, and removal modifiers follow the Livewire 3 behavior.

For page-level notifier messages driven by a PHP configuration map, see
[Magewire Loaders](../advanced/javascript/features/magewire-loaders.md).
