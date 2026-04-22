# Actions

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/actions") }}

## Defining an action

Components extend `Magewirephp\Magewire\Component`; actions are public methods.

```php title="Magewire/Counter.php"
<?php

namespace Vendor\Module\Magewire;

class Counter extends \Magewirephp\Magewire\Component
{
    public int $count = 0;

    public function increment(): void
    {
        $this->count++;
    }
}
```

```html title="view/frontend/templates/magewire/counter.phtml"
<div>
    Count: <?= (int) $magewire->count ?>
    <button type="button" wire:click="increment">+1</button>
</div>
```

## Authorisation

Public methods are a public API. Authorise with Magento primitives:

```php
public function archive(int $id): void
{
    if (! $this->authorization->isAllowed('Vendor_Module::archive')) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
    }
}

public function boot(): void
{
    if (! $this->customerSession->isLoggedIn()) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Login required.'));
    }
}
```

## Rate limiting

`SupportMagewireRateLimiting` throttles abusive clients. Configure per store in the admin. See [Rate limiting](../features/rate-limiting.md).
