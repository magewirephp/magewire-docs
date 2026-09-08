# Properties

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/properties") }}

## Template access

In the PHTML, the component instance is available as `$magewire`. Always escape output with Magento's `$escaper`:

```html title="view/frontend/templates/magewire/counter.phtml"
<div>
    <?= $escaper->escapeHtml($magewire->label) ?>: <?= (int) $magewire->count ?>
</div>
```

## Supported types

Magewire registers a `\Magento\Framework\DataObject` synthesizer in addition to Livewire's scalar, array,
`\stdClass`, and backed-enum handling.

!!! warning "DataObject round trips in Magewire 3.6"
    The current synthesizer casts the object to an array instead of serializing `getData()`. That does not provide a
    dependable round trip for normal Magento DataObject state. Keep a plain array as the public property and reconstruct
    the DataObject inside the component until the synthesizer is corrected.

Custom value objects require a [synthesizer](../advanced/synthesizers.md).

## wire:model defaults to deferred

!!! info "Migrating from Magewire V1"
    V1's `wire:model` was live-by-default and `.lazy` meant blur. V3 flips the default: `wire:model` defers. Use `.live` for instant sync. See [Upgrade](../getting-started/upgrade.md).
