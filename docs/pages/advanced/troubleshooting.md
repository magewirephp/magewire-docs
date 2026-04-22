# Troubleshooting

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/troubleshooting") }}

## Nothing reacts — Magewire JS never initialised

1. **Dist build present.** `vendor/magewirephp/magewire/dist/` must contain the compiled JS. If missing, run `composer reinstall magewirephp/magewire`.
2. **Script tag emitted.** The `magewire.script` block must render — check that your layout handle extends `default` (or `magewire-admin` in admin).
3. **No JS errors.** A single unhandled error halts Alpine initialisation.

## "Checksum mismatch"

- `app/etc/env.php`'s `crypt/key` changed between the snapshot being issued and the request arriving. Reload the page.
- A proxy or load balancer rewrote the request body.

## Double Alpine

A theme loaded Alpine on top of Magewire's bundle. Remove the theme's Alpine; use Magewire's bundle only.

## Admin components never mount

Check `setup:upgrade` ran after installing `magewire-admin`, and that the module is enabled: `bin/magento module:status Magewirephp_MagewireAdmin`. See [Admin → How it works](../admin/how-it-works.md).

## "Class not found" after installing magewire-admin

Run `composer dump-autoload`, then `bin/magento setup:upgrade`, then `bin/magento cache:flush`.

## Debug mode

Enable Magento developer mode and spy on `magewire:init`, `commit`, and `morph.updating` hooks in the browser console.

## Still stuck

- Search the [GitHub issues](https://github.com/magewirephp/magewire/issues).
- Open a new issue with: Magento version, Magewire version, a minimal reproduction, and the exact browser-console error.
