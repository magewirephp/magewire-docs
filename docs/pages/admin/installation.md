# Installation

Install as a composer dependency on any Magewire V3 site.

## Requirements

- Magewire core (`magewirephp/magewire`) installed and enabled.
- Magento 2.4.4+ with the admin (Magento_Backend) module enabled.
- PHP 8.2+.

## Install

```
composer require magewirephp/magewire-admin
bin/magento module:enable Magewirephp_MagewireAdmin
bin/magento setup:upgrade
bin/magento setup:di:compile         # production mode only
bin/magento cache:flush
```

In developer mode, the module picks up on the next request — no DI compile needed.

## Verify

Log into the admin. Open the browser devtools Network tab and navigate any admin page. Look for:

- A `<script>` for the Magewire bundle in the response HTML.
- No console errors from `RequireJS` or `Alpine`.

Then check that the module is enabled:

```
bin/magento module:status Magewirephp_MagewireAdmin
```

Expected output includes `Magewirephp_MagewireAdmin` under **enabled**.

## What gets registered

On install the package adds:

| File | Effect |
|---|---|
| `etc/adminhtml/routes.xml` | Admin router `magewire` mapped to the `frontName` `magewire` under the admin prefix |
| `etc/adminhtml/di.xml` | Replaces core view model + resolver with admin-aware variants; registers the Renderer plugin |
| `view/adminhtml/layout/default.xml` | Injects `magewire.head` and `magewire.script` blocks into the admin layout |

See [How it works](how-it-works.md) for the detail.

## Uninstall

```
composer remove magewirephp/magewire-admin
bin/magento setup:upgrade
bin/magento cache:flush
```

Admin components stop working; storefront components are unaffected.

## Related

- [How it works](how-it-works.md)
- [Building admin components](building-admin-components.md)
