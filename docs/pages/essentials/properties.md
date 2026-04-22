# Properties

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/properties") }}

## Template access

In the PHTML, the component instance is available as `$magewire`. Always escape output with Magento's `$escaper`:

```html title="view/frontend/templates/magewire/counter.phtml"
<div>
    <?= $escaper->escapeHtml($magewire->label) ?>: <?= (int) $magewire->count ?>
</div>
```

## Supported types

In addition to the Livewire defaults, Magewire supports `\Magento\Framework\DataObject` out of the box (serialised via `getData()`). Custom value objects require a [synthesizer](../advanced/synthesizers.md).

## wire:model defaults to deferred

!!! info "Migrating from Magewire V1"
    V1's `wire:model` was live-by-default and `.lazy` meant blur. V3 flips the default — `wire:model` defers. Use `.live` for instant sync. See [Upgrade](../getting-started/upgrade.md).
