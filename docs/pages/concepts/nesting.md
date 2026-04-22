# Nesting

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/nesting") }}

## Layout-driven children

A nested component is a Magento layout block bound to a Magewire class. Children are rendered via `$block->getChildHtml('name')`; each child emits its own `<wire:snapshot>`. Identity across morphs is matched by the block's layout name (and `wire:key` inside loops).

```html
<?php foreach ($magewire->lines as $line): ?>
    <div wire:key="line-<?= (int) $line['id'] ?>">
        <?= $block->getChildHtml('line-' . $line['id']) ?>
    </div>
<?php endforeach; ?>
```

## Flakes vs. nested components

| Aspect | Nested component | Flake |
|---|---|---|
| Own snapshot | Yes | No |
| Own request cycle | Yes | No |
| Layout block required | Yes | Registered in `magewire_flakes.xml` |
| Nesting inside nesting | Yes | Not supported |

See [Flakes](../features/magewire-flakes.md).
