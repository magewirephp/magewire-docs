# wire:dirty

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-dirty") }}

`wire:dirty` reacts when the component's browser-side value differs from the last server-confirmed value. It is useful
for unsaved-change labels and field styling.

```php
<input type="text" wire:model="displayName" wire:dirty.class="field-changed">

<span wire:dirty wire:target="displayName">
    <?= $escaper->escapeHtml(__('Unsaved changes')) ?>
</span>
```

When placed on an element with `wire:model`, the directive watches that property automatically. Use `wire:target` to
watch one or more named properties from another element. Magewire clears the dirty state after the server response is
merged.

Dirty state is only a UI comparison. It does not replace server-side validation, persistence checks, or protection
against concurrent changes.
