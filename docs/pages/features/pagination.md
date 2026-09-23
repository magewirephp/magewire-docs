# Pagination

{{ include("admonition/magewire-specific.md", since_version="3.6.0") }}

The `WithPagination` trait tracks page numbers and provides actions such as
`nextPage()` and `previousPage()`. Your component supplies the records and the
last-page boundary.

## Add pagination to a component

This small catalog keeps its data in memory so you can try the controls
without a database query. Use `getPage()` to select the current slice:

```php
<?php

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Component;
use Magewirephp\Magewire\WithPagination;

class ProductList extends Component
{
    use WithPagination;

    private const PER_PAGE = 4;
    private const PRODUCTS = [
        'Notebook', 'Pen', 'Pencil', 'Eraser',
        'Ruler', 'Folder', 'Marker', 'Highlighter',
        'Stapler', 'Tape'
    ];

    /** @return string[] */
    public function getVisibleProducts(): array
    {
        $offset = ((int) $this->getPage() - 1) * self::PER_PAGE;

        return array_slice(self::PRODUCTS, $offset, self::PER_PAGE);
    }

    public function getLastPage(): int
    {
        return (int) ceil(count(self::PRODUCTS) / self::PER_PAGE);
    }
}
```

Render one root element and call the trait's actions from the template:

```php title="view/frontend/templates/magewire/product-list.phtml"
<?php $currentPage = (int) $magewire->getPage() ?>

<div>
    <ul>
        <?php foreach ($magewire->getVisibleProducts() as $product): ?>
            <li wire:key="product-<?= $escaper->escapeHtmlAttr($product) ?>">
                <?= $escaper->escapeHtml($product) ?>
            </li>
        <?php endforeach ?>
    </ul>

    <button type="button" wire:click="previousPage" <?= $currentPage === 1 ? 'disabled' : '' ?>>
        <?= $escaper->escapeHtml(__('Previous')) ?>
    </button>

    <span><?= $escaper->escapeHtml(__('Page %1 of %2', $currentPage, $magewire->getLastPage())) ?></span>

    <button type="button" wire:click="nextPage"
            <?= $currentPage >= $magewire->getLastPage() ? 'disabled' : '' ?>>
        <?= $escaper->escapeHtml(__('Next')) ?>
    </button>
</div>
```

For a real catalog, inject a Magento query service and request only one page
of results with a page size and current page. Avoid loading every product and
then calling `array_slice()`. The last page should come from the same filtered
query as the visible records. The trait does not know your collection size,
so enforce the upper bound in your own action or service if callers can request
arbitrary pages.

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
