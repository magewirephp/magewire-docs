# Properties

Public properties carry a component's state between browser requests. Start
with small scalar values and arrays that describe the interface:

```php title="Magewire/ProductSearch.php"
<?php

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Component;

class ProductSearch extends Component
{
    public string $query = '';
    public array $selectedBrands = [];
    public int $pageSize = 12;

    public function mount(int $pageSize = 12): void
    {
        $this->pageSize = $pageSize;
    }
}
```

The layout can set `pageSize` on the first render with
`magewire:mount:page-size`. Later requests restore public state from the
browser snapshot. Validate values again before using them in a query; an
initial layout value does not make a public property permanently trusted.

## Template access

In PHTML, the component is available as `$magewire`. Escape text and
attributes with Magento's `$escaper`:

```php title="view/frontend/templates/magewire/product-search.phtml"
<div>
    <label for="product-query"><?= $escaper->escapeHtml(__('Search products')) ?></label>
    <input id="product-query"
           type="search"
           wire:model.live.debounce.300ms="query"
           value="<?= $escaper->escapeHtmlAttr($magewire->query) ?>">

    <p><?= $escaper->escapeHtml(__('Showing up to %1 items', $magewire->pageSize)) ?></p>
</div>
```

Use `wire:model` to update a property. A plain binding waits for the next
component request; the `.live` modifier sends requests while the user types.
See [`wire:model`](../html-directives/wire-model.md) for request timing.

## Supported types

Magewire handles scalars and arrays, and registers synthesizers for some
other value types. Prefer an ID or a small array of values over a Magento
model or service object in public state. Inject repositories and services
into the component constructor, then load fresh domain objects on the server.

!!! warning "DataObject round trips in Magewire 3.6"
    The current synthesizer casts the object to an array instead of serializing
    `getData()`. A normal DataObject cannot dependably round-trip through public
    state. Keep its data in a plain array, or keep only its ID and reload it.

Custom value objects require a [synthesizer](../advanced/synthesizers.md).

<a id="wiremodel-defaults-to-deferred"></a>

## Keep secrets and decisions on the server

Do not store tokens, private customer data, or permission decisions in a
public property. A hidden input or a conditionally hidden button is not an
authorization check. Resolve the current user and check access in every
sensitive action. For migration from V1, note that plain `wire:model` is now
deferred; use `.live` when the server must react as the value changes.
