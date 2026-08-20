# Application Container

{{ include("admonition/magewire-specific.md", since_version="3.5.0") }}

Magewire exposes a small Laravel-compatible application container backed by Magento dependency injection. It exists so ported framework code and Magewire extensions can resolve services through a familiar API without bypassing Magento's object manager configuration.

## Resolve a service

Use the `app()` helper with a class or interface name:

```php
use Magento\Customer\Api\CustomerRepositoryInterface;
use function Magewirephp\Magewire\app;

$customers = app(CustomerRepositoryInterface::class);
```

Magento preferences, virtual types, shared instances, and constructor injection remain authoritative. Supplying explicit arguments requests a fresh contextual instance:

```php
$service = app(ExampleService::class, ['mode' => 'preview']);
```

Calling `app()` without an identifier returns `Magewirephp\Magewire\ApplicationContainer`:

```php
$container = app();

if ($container->has(CustomerRepositoryInterface::class)) {
    $customers = $container->get(CustomerRepositoryInterface::class);
}
```

The container implements both PSR-11's `ContainerInterface` and Magento's `ObjectManagerInterface`. It also provides `make()`, `makeWith()`, `bound()`, `singleton()`, and `instance()` for compatibility with ported code.

## Runtime bindings

Runtime bindings are useful for request-scoped extensions and tests:

```php
$container = app();

$container->singleton(ReportInterface::class, Report::class);
$container->instance(ClockInterface::class, $fakeClock);
```

These bindings live only in the shared container instance for the current PHP process. Application-wide bindings still belong in Magento `di.xml`; do not use runtime bindings as a replacement for Magento module configuration.

Magewire also registers the aliases `livewire` and `redirect` for compatibility with the ported runtime. Prefer class and interface names in application code because they remain explicit and work naturally with Magento DI.
