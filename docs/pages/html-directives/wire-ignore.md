# wire:ignore

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-ignore") }}

Use `wire:ignore` when a third-party script owns an element's DOM and Magewire must not morph it:

```html
<div wire:ignore>
    <select data-address-picker></select>
</div>
```

The ignored markup no longer receives server-rendered updates. Synchronize the widget's value deliberately through a
hidden `wire:model`, `$wire.set()`, or a custom browser integration, and destroy the widget when its surrounding
component is removed.

`wire:ignore.self` ignores changes to the element's own attributes while allowing its children to morph.
`wire:ignore.children` preserves its children while allowing the root attributes to update. Use the narrowest form
that protects the third-party widget.
