# Pagination

{{ include("admonition/magewire-specific.md", since_version="3.6.0") }}

The `WithPagination` trait keeps one or more page numbers in synchronized Magewire component state.
It provides navigation methods and lifecycle hooks; the component remains responsible for querying
and rendering the records for its current page.

## Add pagination to a component

Use `Magewirephp\Magewire\WithPagination` and read the current page with `getPage()`:

```php
<?php

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Component;
use Magewirephp\Magewire\WithPagination;

class ProductList extends Component
{
    use WithPagination;

    private const PER_PAGE = 12;

    /** @return string[] */
    public function getVisibleProducts(): array
    {
        $products = $this->loadProductNames();
        $offset = ((int) $this->getPage() - 1) * self::PER_PAGE;

        return array_slice($products, $offset, self::PER_PAGE);
    }

    /** @return string[] */
    private function loadProductNames(): array
    {
        // Load values from the service or collection owned by this component.
        return [];
    }
}
```

Render the current values and call the trait's public actions from the template:

```html
<?php $currentPage = (int) $magewire->getPage() ?>

<ul>
    <?php foreach ($magewire->getVisibleProducts() as $product): ?>
        <li><?= $escaper->escapeHtml($product) ?></li>
    <?php endforeach ?>
</ul>

<button type="button" wire:click="previousPage" <?= $currentPage === 1 ? 'disabled' : '' ?>>
    <?= $escaper->escapeHtml(__('Previous')) ?>
</button>

<span><?= $escaper->escapeHtml(__('Page %1', $currentPage)) ?></span>

<button type="button" wire:click="nextPage">
    <?= $escaper->escapeHtml(__('Next')) ?>
</button>
```

Disable **Next** in real components when the current page reaches the last available page. Magewire
does not know the size of the collection and therefore cannot enforce that boundary automatically.

## Available methods

| Method | Result |
|---|---|
| `getPage($pageName = 'page')` | Return the current page, defaulting to `1`. |
| `previousPage($pageName = 'page')` | Move back one page without going below `1`. |
| `nextPage($pageName = 'page')` | Move forward one page. |
| `gotoPage($page, $pageName = 'page')` | Move to a specific page. |
| `resetPage($pageName = 'page')` | Return the paginator to page `1`. |
| `setPage($page, $pageName = 'page')` | Set state and run paginator lifecycle hooks. |

Numeric values at or below zero are clamped to page `1`.

## Multiple paginators

Pass a stable name when a component owns more than one paginator:

```php
public function getCurrentReviewPage(): int
{
    return (int) $this->getPage('review-page');
}

public function previousReviewPage(): void
{
    $this->previousPage('review-page');
}

public function nextReviewPage(): void
{
    $this->nextPage('review-page');
}
```

The default paginator remains available under `page`; the named paginator above is stored under
`review-page`. Use wrapper actions when they make template intent clearer.

## Lifecycle hooks

`setPage()` calls generic hooks for every paginator:

```php
public function updatingPaginators(int $page, string $pageName): void
{
}

public function updatedPaginators(int $page, string $pageName): void
{
}
```

It also calls hooks derived from the paginator name. The default `page` paginator uses
`updatingPage()` and `updatedPage()`; `review-page` uses `updatingReviewPage()` and
`updatedReviewPage()`:

```php
public function updatedPage(int $page): void
{
    // React to the default paginator.
}

public function updatedReviewPage(int $page): void
{
    // React to the named paginator.
}
```

## Magewire 3.6 limitations

Pagination in 3.6 deliberately covers component state and navigation only:

- page numbers are not synchronized with the browser URL or query string;
- a reload starts the component at page `1` unless the component restores state itself;
- Magewire does not provide paginator templates or override Magento/Laravel paginator views;
- `WithoutUrlPagination` is present for upstream compatibility but does not change behavior because
  URL pagination is not enabled;
- the component must query, slice, and render the current result set itself.

These differences mean Livewire pagination examples that depend on `$records->links()` or URL-backed
page state cannot be copied directly into Magewire 3.6.

## Related

- [Actions](../essentials/actions.md): invoking page navigation from the template.
- [Lifecycle Hooks](../essentials/lifecycle-hooks.md): reacting to synchronized state changes.
- [Request Bundling](request-bundling.md): how component updates share browser requests.
