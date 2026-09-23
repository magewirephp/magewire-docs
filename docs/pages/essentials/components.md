# Components

Build a component with a PHP class, a PHTML template, and a Magento layout
block. Magewire resolves the class from the block's `magewire` argument and
passes it to the template as `$magewire`.

<a id="creating-components"></a>

## Create your first component

{{ include("create-a-component.md") }}

<a id="block-arguments"></a>
<a id="binding-a-component"></a>

## Pass initial values from layout

Prefix an argument with `magewire:mount:` to pass a named value to `mount()`.
This makes the same class reusable on different pages:

```xml title="view/frontend/layout/catalog_category_view.xml"
<block name="vendor.module.category-products"
       template="Vendor_Module::magewire/category-products.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object" shared="false">
            Vendor\Module\Magewire\CategoryProducts
        </argument>
        <argument name="magewire:mount:category-id" xsi:type="number">10</argument>
        <argument name="magewire:mount:page-size" xsi:type="number">20</argument>
    </arguments>
</block>
```

```php title="Magewire/CategoryProducts.php"
<?php

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Component;

class CategoryProducts extends Component
{
    public int $categoryId = 0;
    public int $pageSize = 10;

    public function mount(int $categoryId, int $pageSize = 10): void
    {
        $this->categoryId = $categoryId;
        $this->pageSize = $pageSize;
    }
}
```

Magewire converts the `category-id` and `page-size` suffixes to `$categoryId`
and `$pageSize`. `mount()` runs on the first render. On later requests, Magewire
restores public state from the snapshot, so treat both values as untrusted when
using them in a query or action. Resolve the current category and check its
visibility through your Magento service.

## Reuse the class safely

Each rendered block needs a unique `name` and an independent component instance.
Set `shared="false"` on the Magento object argument when a class is bound more
than once. Give each block its own `magewire:mount:*` values:

```xml
<block name="vendor.module.featured" template="Vendor_Module::magewire/category-products.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object" shared="false">Vendor\Module\Magewire\CategoryProducts</argument>
        <argument name="magewire:mount:category-id" xsi:type="number">10</argument>
    </arguments>
</block>
<block name="vendor.module.sale" template="Vendor_Module::magewire/category-products.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object" shared="false">Vendor\Module\Magewire\CategoryProducts</argument>
        <argument name="magewire:mount:category-id" xsi:type="number">20</argument>
    </arguments>
</block>
```

<a id="group-arguments"></a>
<a id="reserved-keys"></a>
<a id="public-arguments"></a>

## Advanced block arguments

Custom resolvers and features can read grouped arguments through the argument
API. Application components usually only need `magewire:mount:*`.

```xml
<argument name="magewire:config:cache-ttl" xsi:type="number">3600</argument>
```

```php
$arguments->forMount()->all();          // ['categoryId' => 10, 'pageSize' => 20]
$arguments->forGroup('config')->all();  // ['cacheTtl' => 3600]
```

Use `magewire:alias` only when you need a stable component lookup alias, and
`magewire:resolver` only for a custom resolver. The older array binding with a
`type` item is retained for migration but marked deprecated in the V3 resolver.
A boolean `type` item cannot construct a component. The `magewire.*` namespace
is parsed but does not initialize public properties; use `mount()` instead.

See [Resolvers](../advanced/architecture/mechanisms/resolvers.md) for custom
binding and [Properties](properties.md) for public state.
