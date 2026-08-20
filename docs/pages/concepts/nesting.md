# Nesting

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/nesting") }}

## Layout-driven children

A nested component is a Magento layout block bound to a Magewire class. Children are rendered via `$block->getChildHtml('name')`; each child emits its own `<wire:snapshot>`. Identity across morphs is matched by the block's layout name (and `wire:key` inside loops).

```html
<?php foreach ($magewire->lines as $line): ?>
    <div wire:key="line-<?= (int) $line['id'] ?>">
        <?= $block->getChildHtml('line-' . $line['id']) ?>
    </div>
<?php endforeach; ?>
```

## Lightweight child markup

Not every child block needs to be a Magewire component. Render a normal Magento child block when it only contributes markup to the parent's snapshot. The experimental Flakes source is not currently a stable alternative and is intentionally omitted from navigation.
