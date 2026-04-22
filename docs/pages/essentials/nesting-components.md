# Nesting Components

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/nesting") }}

## Layout XML

Nest Magewire children under a parent block in layout XML:

```xml title="view/frontend/layout/catalog_product_view.xml"
<referenceBlock name="content">
    <block name="product.toolbar"
           template="Vendor_Module::magewire/product/toolbar.phtml">
        <arguments>
            <argument name="magewire" xsi:type="object">
                Vendor\Module\Magewire\Product\Toolbar
            </argument>
        </arguments>

        <block name="product.toolbar.cart-button"
               as="cart-button"
               template="Vendor_Module::magewire/product/cart-button.phtml">
            <arguments>
                <argument name="magewire" xsi:type="object">
                    Vendor\Module\Magewire\Product\CartButton
                </argument>
            </arguments>
        </block>
    </block>
</referenceBlock>
```

## Rendering children

Use `$block->getChildHtml('alias')` from the parent template. Each child emits its own `<wire:snapshot>`.

```html title="templates/magewire/product/toolbar.phtml"
<div>
    <h1><?= $escaper->escapeHtml($magewire->productName) ?></h1>
    <?= $block->getChildHtml('cart-button') ?>
</div>
```

## Keyed children in loops

```html
<?php foreach ($magewire->lines as $line): ?>
    <?= $block->getChildHtml('line-' . $line['id']) ?>
<?php endforeach; ?>
```

For dynamically-created child blocks, generate them in `mount()` or a hook with unique `name` / `as` aliases.

## Flakes

A child without full component isolation belongs as a [Flake](../features/magewire-flakes.md).
