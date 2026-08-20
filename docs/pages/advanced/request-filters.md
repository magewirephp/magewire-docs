# Request Filters

{{ include("admonition/magewire-specific.md", since_version="3.5.0") }}

Request filters reject invalid or unwanted Magewire update requests before any component is reconstructed. A filter runs once per HTTP request, so it is the right layer for checks that protect every component in a bundled request.

## Create a filter

Implement `RequestFilterInterface` and throw a `RequestFilterException` subclass to stop the request:

```php
<?php

namespace Vendor\Module\Magewire\Filter;

use Magewirephp\Magewire\Exceptions\RequestFilterException;
use Magewirephp\Magewire\Mechanisms\HandleRequests\Filter\RequestFilterInterface;
use Magewirephp\Magewire\Mechanisms\HandleRequests\RequestContext;

final class MaintenanceFilter implements RequestFilterInterface
{
    public function __construct(
        private readonly MaintenanceMode $maintenanceMode,
    ) {
    }

    public function check(RequestContext $context): void
    {
        if ($this->maintenanceMode->isEnabled()) {
            throw new MaintenanceRequestException((string) __('Please try again shortly.'));
        }
    }
}

final class MaintenanceRequestException extends RequestFilterException
{
    public function status(): int
    {
        return 503;
    }
}
```

`RequestContext` provides:

- `getRequest()` — the Magento HTTP request.
- `getComponents()` — component request contexts in payload order.
- `getToken()` — the already verified form key.
- `getFingerprint()` — an opaque identifier for the request origin.
- `attributes()` — request-scoped data that filters can share.

Filters should be inexpensive and must not reconstruct, hydrate, or render components.

## Register a filter

Add it to the request filter pipeline in `etc/frontend/di.xml`:

```xml
<type name="Magewirephp\Magewire\Mechanisms\HandleRequests\Filter\RequestFilterPipeline">
    <arguments>
        <argument name="filters" xsi:type="array">
            <item name="vendor_maintenance" xsi:type="object">Vendor\Module\Magewire\Filter\MaintenanceFilter</item>
        </argument>
    </arguments>
</type>
```

Magento's merged array order determines filter order. Use stable item names and module sequencing when one filter depends on another.

## Safe browser messages

Magewire's request-filter exception handler returns the exception's status and message, together with the `X-Magewire-Message-Severity` response header. The browser only presents a failed response as a customer message when that header is present. Unhandled error pages and stack traces therefore stay in the normal failure path and are not shown as notifications.

Override `severity()` on the exception when the default warning severity is not appropriate. The built-in request-scoped rate limiter uses this same filter pipeline; component-scoped rate limiting still runs during component reconstruction.
