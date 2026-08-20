# wire:poll

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-poll") }}

`wire:poll` refreshes a component or calls an action on an interval:

```php
<div wire:poll.15s="refreshStatus">
    <?= $escaper->escapeHtml($magewire->statusLabel) ?>
</div>
```

The default interval is two seconds. Use an explicit interval appropriate for Magento's application and database load.
The `.visible` modifier pauses polling while the element is outside the viewport. Background tabs are heavily
throttled unless `.keep-alive` is present, and polling pauses while the browser reports that it is offline.

Polling creates normal component requests, so caching, rate limiting, authorization, and observability still apply.
For frequently changing global data, consider whether a purpose-built push or cached endpoint is a better fit than many
simultaneous customer sessions polling Magento.
