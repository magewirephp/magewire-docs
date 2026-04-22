# wire:stream

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/wire-stream") }}

## Magento output buffering

Magewire disables output buffering on the update controller for streaming actions, but Magento's FPC and some hosting layers (Varnish, Cloudflare) may still buffer the response. If `wire:stream` updates arrive only at the end, check:

1. PHP `output_buffering` in `php.ini` or FPM pool
2. `ob_*` calls from observers / plugins
3. Nginx `proxy_buffering`
4. Varnish buffering on the admin / storefront host
