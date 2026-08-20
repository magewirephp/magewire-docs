# wire:cloak

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-cloak") }}

`wire:cloak` marks content that should remain hidden until Magewire initializes, then the browser runtime removes the
attribute.

```php
<div wire:cloak>
    <?= $escaper->escapeHtml(__('Reactive account controls are ready.')) ?>
</div>
```

!!! warning "Add the hiding rule in Magewire 3.5"
    Magewire 3.5 removes `wire:cloak`, but its base CSS only defines the equivalent `x-cloak` rule. Add the following
    rule to your theme until core supplies it:

    ```css
    [wire\:cloak] {
        display: none !important;
    }
    ```

Do not cloak essential content that must remain usable when JavaScript fails. For Alpine-owned markup, use `x-cloak`
with the rule already supplied by Magewire's base styles.
