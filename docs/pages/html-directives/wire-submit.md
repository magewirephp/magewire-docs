# wire:submit

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-submit") }}

Attach `wire:submit` to a form to prevent the normal browser submission and call a component action. Deferred
`wire:model` values in the form are included in the same commit.

```php title="view/frontend/templates/magewire/profile.phtml"
<form wire:submit="save">
    <label for="display-name">
        <?= $escaper->escapeHtml(__('Display name')) ?>
    </label>
    <input id="display-name" type="text" wire:model="displayName">

    <button type="submit">
        <?= $escaper->escapeHtml(__('Save')) ?>
    </button>
</form>
```

Magewire temporarily disables submit buttons, selects, checkboxes, and radio buttons and makes text fields read-only
while the submission is in flight. Use [`wire:loading`](wire-loading.md) for an explicit progress label.

The action remains a normal public PHP method. Validate its properties, authorize the operation, and render validation
messages in the component rather than relying on browser validation alone.
