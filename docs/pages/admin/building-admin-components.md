# Building Admin Components

Admin components are Magewire components registered in the admin area. The PHP class, the template, and the lifecycle are identical to storefront components — only the DI scope and the layout directory differ.

## File layout

```
Vendor/Module/
├── etc/
│   └── adminhtml/
│       └── di.xml                         # Feature / resolver / hook registrations
├── Magewire/
│   └── Admin/
│       └── OrderEditor.php                # Component class
├── view/
│   └── adminhtml/
│       ├── layout/
│       │   └── sales_order_view.xml       # Bind component to a block
│       └── templates/
│           └── magewire/
│               └── admin/
│                   └── order-editor.phtml # Template
```

Storefront components go in `view/frontend/…`; admin components go in `view/adminhtml/…`. The convention is identical otherwise.

## Example: a simple admin component

```php title="Magewire/Admin/OrderStatusEditor.php"
<?php

namespace Vendor\Module\Magewire\Admin;

use Magewirephp\Magewire\Component;

class OrderStatusEditor extends Component
{
    public int $orderId = 0;
    public string $status = '';
    public string $note = '';

    public function mount(int $orderId, string $currentStatus): void
    {
        $this->orderId = $orderId;
        $this->status = $currentStatus;
    }

    public function save(): void
    {
        if (! $this->authorization->isAllowed('Magento_Sales::edit')) {
            throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
        }

        $this->orderService->updateStatus($this->orderId, $this->status, $this->note);

        $this->magewireNotifications()
            ->make(__('Order %1 updated.', $this->orderId))
            ->asSuccess();
    }
}
```

## Binding to an admin block

```xml title="view/adminhtml/layout/sales_order_view.xml"
<?xml version="1.0"?>
<page xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="urn:magento:framework:View/Layout/etc/page_configuration.xsd">
    <body>
        <referenceContainer name="left">
            <block name="magewire.admin.order-status"
                   template="Vendor_Module::magewire/admin/order-status.phtml">
                <arguments>
                    <argument name="magewire" xsi:type="object">
                        Vendor\Module\Magewire\Admin\OrderStatusEditor
                    </argument>
                    <argument name="magewire:mount:orderId" xsi:type="string">
                        ${order_id}
                    </argument>
                    <argument name="magewire:mount:currentStatus" xsi:type="string">
                        ${order_status}
                    </argument>
                </arguments>
            </block>
        </referenceContainer>
    </body>
</page>
```

Notes:

- The argument name stays `magewire` — same as storefront. `magewire-admin` registers `LayoutAdminResolver` with a higher sort order in `adminhtml/di.xml`, so it runs before the default `LayoutResolver` and claims admin-area blocks automatically. The `layout_admin` string is the resolver's internal accessor (stored in the snapshot memo for reconstruction), not a layout XML argument name.
- `magewire:mount:*` arguments are passed to the component's `mount()` method.

## Template

```html title="view/adminhtml/templates/magewire/admin/order-status.phtml"
<div>
    <select wire:model="status">
        <option value="pending">Pending</option>
        <option value="processing">Processing</option>
        <option value="complete">Complete</option>
    </select>

    <textarea wire:model="note"
              placeholder="<?= $escaper->escapeHtmlAttr(__('Optional note')) ?>"></textarea>

    <button wire:click="save" wire:loading.attr="disabled">
        <?= $escaper->escapeHtml(__('Save')) ?>
    </button>
</div>
```

Standard Magewire syntax — no admin-specific directives.

## Authorization

Public methods on an admin component are callable by any admin user whose session passes the route's cookie check. **That is not enough for sensitive actions.** Check ACL inside every method that touches data:

```php
public function refund(int $orderId): void
{
    if (! $this->authorization->isAllowed('Magento_Sales::refund')) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
    }
    // …
}
```

For component-wide checks, use `boot()`:

```php
public function boot(): void
{
    if (! $this->authorization->isAllowed('Vendor_Module::some_resource')) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
    }
}
```

## Registering admin-scoped Features

Any Feature / Component Hook / Synthesizer the component depends on must be registered in `etc/adminhtml/di.xml` — the area-scoped equivalent of the storefront's `etc/frontend/di.xml`.

```xml title="etc/adminhtml/di.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:ObjectManager/etc/config.xsd">
    <type name="Magewirephp\Magewire\MagewireServiceProvider">
        <arguments>
            <argument name="features" xsi:type="array">
                <item name="support_my_admin_feature" xsi:type="string">
                    Vendor\Module\Magewire\Features\SupportMyAdminFeature
                </item>
            </argument>
        </arguments>
    </type>
</config>
```

## Gotchas

- **No Tailwind.** The admin theme ships its own styles. Use admin-compatible CSS; do not rely on Tailwind utility classes.
- **Prototype.js.** Some admin pages still include Prototype. Magewire-admin restores `Object.keys` / `Object.values`, but other Prototype-era APIs (`Element.observe`, `Hash`) are out there. Avoid them in component JavaScript.
- **RequireJS ordering.** Admin modules often depend on RequireJS. Magewire-admin forces its bundle to load first — as long as your own admin scripts don't `requirejs.config()` in a way that overrides global shim order, you are fine.
- **Full-page cache.** The admin is not FPC-cached, so CSP nonces (not hashes) are used on every request.

## Related

- [How it works](how-it-works.md)
- [Security](../advanced/security.md)
- [Rate limiting](rate-limiting.md)
