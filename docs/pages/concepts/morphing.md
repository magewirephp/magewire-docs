# Morphing

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/morphing") }}

## Keyed loop items

Use Magento-typed escapers and PHP loops when keying items:

```html
<?php foreach ($magewire->products as $product): ?>
    <div wire:key="product-<?= (int) $product['id'] ?>">
        <?= $escaper->escapeHtml($product['name']) ?>
    </div>
<?php endforeach; ?>
```

## Morph hooks

Magewire exposes morph hooks through the `magewire:init` event:

```javascript
document.addEventListener('magewire:init', () => {
    Magewire.hook('morph.updating', ({ el, component, toEl, skip, childrenOnly }) => {});
    Magewire.hook('morph.removed', ({ el, component }) => {});
});
```
