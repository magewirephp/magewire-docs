# wire:offline

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-offline") }}

`wire:offline` toggles an element when the browser emits its offline and online events:

```php
<p wire:offline role="status">
    <?= $escaper->escapeHtml(__('You are offline.')) ?>
</p>
```

Magewire's base CSS hides a plain offline element initially. The `.class`, `.attr`, and `.remove` modifiers can update an
existing control instead. Detection reflects browser network state only; it is not a health check for Magento or the
Magewire update route.

See [Offline States](../features/offline-states.md) for failure-handling and polling considerations.
