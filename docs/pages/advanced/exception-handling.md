# Exception Handling

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

When a component throws — during the initial page render or during an update — Magewire catches it
and routes it through a configurable **exception pipeline** instead of letting it blow up the page or
the XHR. You can observe it per component, swap the error UI, or bind specific exception types to
custom handlers.

## The two contexts

Handling differs by [request mode](architecture/runtime.md#request-modes):

- **Preceding** (initial page render) — the failing block's template is swapped to
  `Magewirephp_Magewire::magewire/exception.phtml`, so the page renders an error placeholder where
  the component would be instead of crashing the whole page. The component binding is removed from
  the block to prevent a cyclic re-trigger, and the exception is attached to the block as data.
- **Subsequent** (`/magewire/update` XHR) — the exception is normalised (wrapped in a
  `RequestException` if it isn't one already) and returned to the browser, where the JS runtime
  surfaces it.

The active mode is resolved from the runtime, so the same thrown exception is handled appropriately
in each context.

## The `exception()` component hook

The first place to handle an error is the component itself. Define an `exception()`
[lifecycle hook](../essentials/lifecycle-hooks.md); call the provided `$stopPropagation` callback to
swallow the error and continue:

```php
use Throwable;

public function exception(Throwable $e, callable $stopPropagation): void
{
    if ($e instanceof MyRecoverableException) {
        $this->magewireNotifications()->make(__('Something went wrong, please retry.'))->asError();

        $stopPropagation(); // handled — don't bubble further
    }
}
```

## The ExceptionManager

`Magewirephp\Magewire\Model\App\ExceptionManager` (`@api`) is the central router. It holds a default
**preceding** handler and a default **subsequent** handler, plus a pool of **type-specific** handlers
keyed by exception class — optionally scoped to a context group.

A handler can do one of three things by what it returns from `handle()`:

- **Return a (different) exception** — that exception is logged and thrown.
- **Return a callable** — used as a custom response builder (the request flow runs it instead of
  throwing). Useful for turning an exception into a specific HTTP response.
- **Throw / return a `SilentException`** — the error is swallowed silently (logged, not surfaced).

`RequestException` is the wrapper used for subsequent-mode errors; `SilentException` is the
"swallow this" signal.

## Writing a custom handler

Extend `AbstractExceptionHandler` and override `handle()` (response/normalisation) and/or
`handleWithBlock()` (the rendered placeholder during a page render):

```php
namespace Vendor\Module\Magewire\Exception;

use Exception;
use Magento\Framework\App\Response\HttpInterface as HttpResponseInterface;
use Magewirephp\Magewire\Model\App\AbstractExceptionHandler;

class TooManyRequestsHandler extends AbstractExceptionHandler
{
    public function handle(Exception $exception, bool $subsequent = false): Exception|callable
    {
        // Turn the exception into a 429 response instead of throwing.
        return static function (HttpResponseInterface $response) {
            $response->setBody('Too Many Requests.');
            $response->setHttpResponseCode(429);

            return $response;
        };
    }
}
```

Register it in the `specificExceptionHandlerPool`, keyed by exception class. Nest it under
`subsequent` or `preceding` to scope it to one context, or place it at the top level to apply to
both:

```xml title="etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Model\App\ExceptionManager">
    <arguments>
        <argument name="specificExceptionHandlerPool" xsi:type="array">
            <item name="subsequent" xsi:type="array">
                <item name="Vendor\Module\Exception\TooManyRequestsException" xsi:type="object">
                    Vendor\Module\Magewire\Exception\TooManyRequestsHandler
                </item>
            </item>
        </argument>
    </arguments>
</type>
```

This is exactly how the rate-limiting feature plugs in: it binds its `TooManyRequestsException` to a
handler that returns a `429` response on update requests. See [Rate Limiting](../features/rate-limiting.md).

## The error placeholder template

The default preceding-mode handler points the block at
`Magewirephp_Magewire::magewire/exception.phtml` and passes along the application state. Because the
state is available, the template can show full exception detail in
[developer mode](../essentials/view-model.md) and a quiet, generic message in
production. Override the template (per the [Layout](architecture/layout.md) override rules) to
style or restyle the placeholder for your theme.

## Related

- [Troubleshooting](troubleshooting.md) — diagnosing common runtime errors.
- [Rate Limiting](../features/rate-limiting.md) — a real custom handler in core.
- [Runtime](architecture/runtime.md) — preceding vs subsequent request modes.
- [Lifecycle Hooks](../essentials/lifecycle-hooks.md) — the `exception()` hook.