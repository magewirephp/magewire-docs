# Lifecycle Hooks

Lifecycle hooks let a component prepare initial state, check each request, and
react to property updates. The hooks live on the same PHP class as its actions.

| Hook | When it runs | Typical use |
|---|---|---|
| `mount()` | Initial render | Convert layout arguments into public state. |
| `boot()` | Initial render and updates | Resolve the current user and enforce access. |
| `hydrate()` | After state is restored on an update | Rebuild request-local state. |
| `updatedQuery()` | After `query` changes | Reset a paginator or dependent UI state. |
| `rendering()` | Before PHTML renders | Select a template for the current state. |

## mount() receives layout XML arguments

`mount()` receives `magewire:mount:*` layout arguments as named parameters:

```xml
<argument name="magewire:mount:product-id" xsi:type="number">42</argument>
```

```php
public int $productId = 0;

public function mount(int $productId): void
{
    $this->productId = $productId;
}
```

`mount()` does not run again on a Magewire update. Reload the product from a
repository when a later action needs it, and check that the current visitor
may access it. Public `productId` is restored from browser-visible state.

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

Use an action-specific check as well if some methods need a stronger
permission. A plain `initialize()` method is not a public component
lifecycle hook.

## React to a changed property

When a query changes, returning to the first page keeps the result list
consistent. This component uses Magewire's `WithPagination` trait:

```php
use Magewirephp\Magewire\WithPagination;

class ProductList extends \Magewirephp\Magewire\Component
{
    use WithPagination;

    public string $query = '';

    public function updatedQuery(string $value): void
    {
        $this->resetPage();
    }
}
```

Pair this with `wire:model.live.debounce.300ms="query"` in the template.
See [Pagination](../features/pagination.md) for querying and page controls.

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

## Hooks are not actions

The browser cannot call a lifecycle hook, and an event listener cannot point at one. Since Magewire 3.7.2, these names
are reserved:

- `boot`, `booted`, `mount`, `exception`, `rendering`, `rendered`, and `placeholder`;
- any name starting with `hydrate`, `dehydrate`, `updating`, or `updated`;
- trait hooks, such as `bootWithPagination`: a hook name followed by the basename of a trait the component uses.

Names are matched case-sensitively, so declare hooks in the casing shown. If an action uses one of these names, rename
it. See [Upgrade notes](../getting-started/releases/upgrade-notes.md#reserved-method-names) for the full list.

<a id="exception-handling-with-notifications"></a>

For exception handling, show a safe customer-facing message and let
authorization failures propagate. Do not translate or display arbitrary
exception messages. See [Exception handling](../advanced/exception-handling.md).
