# wire:click

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-click") }}

Use `wire:click` to call a public component method when an element is clicked:

```php title="view/frontend/templates/magewire/counter.phtml"
<button type="button" wire:click="increment">
    <?= $escaper->escapeHtml(__('Increase')) ?>
</button>
```

Arguments can be passed in the expression, but they originate in browser-controlled markup. Resolve sensitive entities
again on the server and authorize the action instead of trusting an ID because it appeared in the template.

```html
<button type="button" wire:click="remove(42)">Remove</button>
```

Event modifiers such as `.prevent`, `.stop`, `.once`, and `.debounce` are handled through Alpine. Refer to the Livewire
3 page for the complete modifier syntax. Combine the action with [`wire:loading`](wire-loading.md) when the control
needs visible pending state.
