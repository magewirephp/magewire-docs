# wire:stream

`wire:stream` marks an element as the destination for content sent while an
action is still running. This can show progress during a long request.

```php title="Magewire/ImportPreview.php"
<?php

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Component;

class ImportPreview extends Component
{
    public function preview(): void
    {
        $this->stream('preview-status', (string) __('Reading the file…'), true);

        // Call your Magento import-preview service here.
        // Keep actual imports and irreversible work in a dedicated service.

        $this->stream('preview-status', (string) __('Preview ready.'), true);
    }
}
```

```php title="view/frontend/templates/magewire/import-preview.phtml"
<div>
    <button type="button" wire:click="preview">
        <?= $escaper->escapeHtml(__('Preview import')) ?>
    </button>
    <p wire:stream="preview-status" role="status"></p>
</div>
```

The third `stream()` argument replaces earlier content instead of appending.
Do not assume that streamed output has reached the browser until the
transport and hosting stack have been tested.

## Magento output buffering

Magewire disables output buffering on the update controller for streaming
actions, but PHP, the web server, or a proxy may still buffer the response. If
updates appear only after the action finishes, check:

1. PHP `output_buffering` in `php.ini` or the FPM pool;
2. `ob_*` calls from observers or plugins;
3. web-server proxy buffering;
4. Varnish or CDN buffering on the update route.

Streaming changes how progress is displayed; it does not replace
authorization, validation, or a job queue for work that outlives the request.
