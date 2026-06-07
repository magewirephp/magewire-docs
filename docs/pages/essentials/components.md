# Components

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/components") }}

## Creating components

Creating a basic Magewire component takes just a few minutes and requires only two or three files, depending on whether
you already have a layout handle. At its core, a Magewire component consists of two main files: a PHP class that handles
the logic and a template responsible for rendering the HTML on the frontend.

In the following example, we assume you are using layout XML to inject a Magewire component onto a page.
For more advanced use cases, we recommend exploring the in-depth documentation, where concepts like the
[resolver](../advanced/architecture/mechanisms/resolvers.md) mechanism will most likely play a role.

{{ include("create-a-component.md") }}

## Block arguments

Magewire components are bound to Magento blocks through layout XML `<argument>` entries. Beyond the
`magewire` argument that declares the component itself, a structured argument system lets you pass data
straight into a component from layout XML—no custom ViewModel or constructor wiring required.

Arguments are extracted from the block during the assembly phase, after the component has been resolved and
mounted.

### Binding a component

The `magewire` argument tells the [resolver](../advanced/architecture/mechanisms/resolvers.md) which component
to bind to the block. The built-in `LayoutResolver` accepts three formats:

```xml
<!-- 1. Direct object binding (most common) -->
<argument name="magewire" xsi:type="object">Vendor\Module\Magewire\MyComponent</argument>

<!-- 2. Array with an object type, allowing extra config alongside the component -->
<argument name="magewire" xsi:type="array">
    <item name="type" xsi:type="object">Vendor\Module\Magewire\MyComponent</item>
</argument>

<!-- 3. Array with a boolean type for a dynamic component with no physical class -->
<argument name="magewire" xsi:type="array">
    <item name="type" xsi:type="boolean">true</item>
</argument>
```

### Public arguments

Arguments prefixed with `magewire.` become component properties. The prefix is stripped and the kebab-case
key is converted to camelCase before it is matched against a public property on the component.

```xml
<block name="my.component" template="Vendor_Module::my-component.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object">Vendor\Module\Magewire\MyComponent</argument>
        <argument name="magewire.product-id" xsi:type="number">42</argument>
        <argument name="magewire.sort-order" xsi:type="string">price</argument>
    </arguments>
</block>
```

The keys above map as follows:

| Argument | Property |
|---|---|
| `magewire.product-id` | `$productId` |
| `magewire.sort-order` | `$sortOrder` |

### Group arguments

Arguments prefixed with `magewire:{group}:{key}` are collected into named groups rather than being assigned
directly to properties. This keeps related values together and lets a component (or resolver) request a whole
group at once.

```xml
<block name="my.component" template="Vendor_Module::my-component.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object">Vendor\Module\Magewire\MyComponent</argument>
        <argument name="magewire:mount:category-id" xsi:type="number">10</argument>
        <argument name="magewire:mount:page-size" xsi:type="number">20</argument>
        <argument name="magewire:config:cache-ttl" xsi:type="number">3600</argument>
    </arguments>
</block>
```

The `mount` group is passed to your component's `mount()` method as named parameters on the initial render:

```php
public function mount(int $categoryId = 0, int $pageSize = 10): void
{
    // $categoryId = 10, $pageSize = 20 (from magewire:mount:*)
}
```

Any group can also be read directly from the argument API inside a resolver or feature:

```php
$arguments->forMount();          // ['categoryId' => 10, 'pageSize' => 20]
$arguments->forGroup('config');  // ['cacheTtl' => 3600]
$arguments->toParams();          // All public arguments as an array
```

### Reserved keys

A few `magewire:` keys are reserved by the framework and are not treated as group arguments:

| Argument | Purpose |
|---|---|
| `magewire:resolver` | Forces a specific resolver for the block, overriding automatic resolution (e.g. `widget`). |
| `magewire:alias` | Sets a component alias used for lookup (e.g. `shipping-form`). |

```xml
<argument name="magewire:resolver" xsi:type="string">widget</argument>
<argument name="magewire:alias" xsi:type="string">shipping-form</argument>
```

For more on how a block becomes a component and how resolvers consume these arguments, see the
[Resolvers](../advanced/architecture/mechanisms/resolvers.md) documentation.
