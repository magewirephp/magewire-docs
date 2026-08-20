# Offline States

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/offline") }}

Magewire listens for the browser's `online` and `offline` events. Use `wire:offline` to reveal a message or change an
element while the browser reports that network access is unavailable:

```php title="view/frontend/templates/magewire/account/form.phtml"
<p wire:offline role="status">
    <?= $escaper->escapeHtml(__('You are offline. Changes cannot be saved yet.')) ?>
</p>

<button type="submit" wire:offline.attr="disabled">
    <?= $escaper->escapeHtml(__('Save')) ?>
</button>
```

Magewire's base CSS hides a plain `wire:offline` element until the offline event fires. The `.class`, `.attr`, and
`.remove` modifiers can alter an existing element instead of toggling its display; see the Livewire reference for their
complete syntax.

## What offline detection means

An offline event describes the browser's network state. It does not prove that Magento, the Magewire update route, or a
specific upstream service is healthy. A captive portal, proxy failure, expired session, or HTTP error can still occur
while the browser considers itself online.

Keep server-side error handling in place and preserve the user's input after a failed request. `wire:offline` is useful
feedback, not a replacement for validation, exception handling, or retry design.

Polling pauses while the runtime is offline and resumes after an `online` event. Magewire does not queue arbitrary
component actions for replay, so do not promise that a click made offline will be submitted automatically later.

See [`wire:offline`](../html-directives/wire-offline.md), [Exception Handling](../advanced/exception-handling.md), and
[Troubleshooting](../advanced/troubleshooting.md).
