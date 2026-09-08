# Lifecycle Hooks

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/lifecycle-hooks") }}

## mount() receives layout XML arguments

`mount()` receives `magewire:mount:*` layout arguments as named parameters:

```php
public function mount(int $productId): void
{
    $this->productId = $productId;
    $this->name = $this->productRepository->getById($productId)->getName();
}
```

## boot() for Magento guards

Run on every request. During an update, Magewire restores public properties before it triggers the lifecycle sequence;
`boot()` then runs before the component's `hydrate()` hook. Use `boot()` for authorisation and dependency resolution:

```php
public function boot(): void
{
    if (! $this->customerSession->isLoggedIn()) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Login required.'));
    }
}
```

Do not add a plain `initialize()` method to a component. Magewire 3.6 calls internal trait initialization hooks with
that name, but does not expose `initialize()` as a component lifecycle hook.

## Swap templates per state

`Component` has no `render()` method: the block's configured PHTML renders automatically. To switch templates based on state, use the `rendering` hook and set the block's template before render:

```php
public function rendering(): void
{
    $this->magewireBlock()->setTemplate(
        $this->state === 'review'
            ? 'Vendor_Module::magewire/review.phtml'
            : 'Vendor_Module::magewire/default.phtml'
    );
}
```

## Exception handling with notifications

```php
public function exception(\Throwable $e, callable $stopPropagation): void
{
    $this->magewireNotifications()
        ->make(__($e->getMessage()))
        ->asError();

    $stopPropagation();
}
```
