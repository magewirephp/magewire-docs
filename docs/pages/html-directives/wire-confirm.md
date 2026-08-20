# wire:confirm

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-confirm") }}

Add `wire:confirm` to an action element when the browser should ask for confirmation before Magewire sends the call:

```php
<button type="button"
        wire:click="deleteAddress"
        wire:confirm="<?= $escaper->escapeHtmlAttr(__('Delete this address?')) ?>">
    <?= $escaper->escapeHtml(__('Delete')) ?>
</button>
```

The `.prompt` modifier can require an exact phrase for especially deliberate actions; its expression contains the
question and expected response separated by `|`. See the Livewire 3 reference for that syntax.

Confirmation runs entirely in the browser and can be bypassed. The component action must still authorize the current
customer or admin user, validate the target, and handle repeated calls safely.
