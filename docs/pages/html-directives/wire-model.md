# wire:model

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-model") }}

`wire:model` binds a form control to a public component property:

```php
<label for="email"><?= $escaper->escapeHtml(__('Email address')) ?></label>
<input id="email" type="email" wire:model="email">
```

A plain binding updates the browser-side component state but does not immediately send a request. Its value is included
in the next action, submit, or explicit commit. Choose a network trigger when the server must react sooner:

| Modifier | Request timing |
|---|---|
| `.live` | While the value changes; text inputs use a 150 ms debounce by default. |
| `.blur` | When the control loses focus. |
| `.change` | When the browser emits a change event. |
| `.lazy` | Supported as an alias for `.change`. |

Use the Livewire 3 reference for casting and debounce modifiers. Bound values are browser-controlled input: validate
them before persistence and do not expose secrets or authorization decisions as public properties.

!!! info "Migrating from Magewire V1"
    V1's `wire:model` synchronized with the server by default. V3 defers a plain binding, and `.live` opts into
    immediate synchronization. `.lazy` remains an alias for `.change`; use `.blur` when focus loss is the intended
    trigger. See [Upgrade](../getting-started/upgrade.md).
