# Building Admin Components

Admin components are Magewire components registered in the admin area. The PHP class, the template, and the lifecycle are identical to storefront components; only the DI scope and the layout directory differ.

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

use Magento\Framework\App\RequestInterface;
use Magento\Framework\AuthorizationInterface;
use Magento\Sales\Api\OrderRepositoryInterface;
use Magewirephp\Magewire\Component;
use Vendor\Module\Model\OrderStatusUpdater;

class OrderStatusEditor extends Component
{
    public int $orderId = 0;
    public string $status = '';
    public string $note = '';

    public function __construct(
        private readonly RequestInterface $request,
        private readonly OrderRepositoryInterface $orders,
        private readonly AuthorizationInterface $authorization,
        private readonly OrderStatusUpdater $orderService
    ) {
    }

    public function mount(): void
    {
        $this->orderId = (int) $this->request->getParam('order_id');
        $order = $this->orders->get($this->orderId);
        $this->status = (string) $order->getStatus();
    }

    public function save(): void
    {
        if (! $this->authorization->isAllowed('Vendor_Module::manage_orders')) {
            throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
        }

        // The service reloads the order and validates this browser-controlled ID.
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
                </arguments>
            </block>
        </referenceContainer>
    </body>
</page>
```

Notes:

- The argument name stays `magewire`, just as on the storefront. `magewire-admin` registers
  `LayoutAdminResolver` at numeric sort order `99800`, before the default `LayoutResolver` at `99900`, so it
  claims admin-area blocks first. The `layout_admin` string is the resolver's internal accessor, not a layout XML
  argument name.
- Magento layout XML does not interpolate placeholders such as `${order_id}`. This example reads the route's
  `order_id` during the initial `mount()`. For another admin route, use its actual request parameter or populate
  concrete block data before Magewire resolves the component.
- Public component properties, including `orderId`, are browser-controlled. The action checks ACL and the write
  service must reload and validate the exact target instead of trusting the hydrated value.

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

Standard Magewire syntax: no admin-specific directives.

## Authorization

Public methods on an admin component are callable by any admin user whose session passes the route's cookie check. **That is not enough for sensitive actions.** Check ACL inside every method that touches data:

```php
public function refund(int $orderId): void
{
    if (! $this->authorization->isAllowed('Vendor_Module::manage_orders')) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
    }
    // …
}
```

For component-wide checks, use `boot()`:

```php
public function boot(): void
{
    if (! $this->authorization->isAllowed('Vendor_Module::manage_orders')) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
    }
}
```

Declare the resource in your module so Magento roles can grant it:

```xml title="etc/acl.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:Acl/etc/acl.xsd">
    <acl>
        <resources>
            <resource id="Magento_Backend::admin">
                <resource id="Vendor_Module::manage_orders"
                          title="Manage module orders"
                          sortOrder="10"/>
            </resource>
        </resources>
    </acl>
</config>
```

`OrderStatusUpdater` in the example is an application service you provide.
It must load the order and enforce allowed status transitions. Keeping that
logic in a service lets a controller or queue consumer use the same rule.

## Registering admin-scoped Features

Register an admin Feature in `etc/adminhtml/di.xml`, the area-scoped equivalent of the storefront's
`etc/frontend/di.xml`. Synthesizers and other extension collections have their own constructor arguments; do not add
them to the Features collection.

```xml title="etc/adminhtml/di.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:ObjectManager/etc/config.xsd">
    <type name="Magewirephp\Magewire\Features">
        <arguments>
            <argument name="items" xsi:type="array">
                <item name="support_my_admin_feature" xsi:type="array">
                    <item name="type" xsi:type="string">
                        Vendor\Module\Magewire\Features\SupportMyAdminFeature
                    </item>
                    <item name="sort_order" xsi:type="number">5000</item>
                </item>
            </argument>
        </arguments>
    </type>
</config>
```

## Gotchas

- **No Tailwind.** The admin theme ships its own styles. Use admin-compatible CSS; do not rely on Tailwind utility classes.
- **Prototype.js.** Some admin pages still include Prototype. Magewire-admin restores `Object.keys` / `Object.values`, but other Prototype-era APIs (`Element.observe`, `Hash`) are out there. Avoid them in component JavaScript.
- **RequireJS ordering.** Admin modules often depend on RequireJS. Magewire-admin forces its bundle to load first. As long as your own admin scripts don't `requirejs.config()` in a way that overrides global shim order, you are fine.
- **Full-page cache.** The admin is not FPC-cached, so CSP nonces (not hashes) are used on every request.

## Related

- [How it works](how-it-works.md)
- [Security](../advanced/security.md)
- [Rate limiting](rate-limiting.md)
