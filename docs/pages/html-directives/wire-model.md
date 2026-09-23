# wire:model

`wire:model` binds an input to a public component property. A plain binding
keeps the browser-side value until the next action or submit request:

```php title="view/frontend/templates/magewire/profile.phtml"
<div>
    <label for="display-name"><?= $escaper->escapeHtml(__('Display name')) ?></label>
    <input id="display-name"
           type="text"
           wire:model="displayName"
           value="<?= $escaper->escapeHtmlAttr($magewire->displayName) ?>">

    <button type="button" wire:click="save">
        <?= $escaper->escapeHtml(__('Save')) ?>
    </button>
</div>
```

The matching component declares `public string $displayName = '';` and a
`save()` action. The action validates the submitted value before using it.

## Choose when to send a request

Use a live binding when server-rendered results should change as the user
types. For a product search, debounce the requests:

```php
<input type="search"
       wire:model.live.debounce.300ms="query"
       value="<?= $escaper->escapeHtmlAttr($magewire->query) ?>">
```

Use `.blur` for a field that should update after the user leaves it:

```php
<input type="text"
       wire:model.blur="postcode"
       value="<?= $escaper->escapeHtmlAttr($magewire->postcode) ?>">
```

| Modifier | Request timing |
|---|---|
| none | On the next action, submit, or explicit commit. |
| `.live` | While the value changes; text inputs use a 150 ms debounce by default. |
| `.blur` | When the control loses focus. |
| `.change` | When the browser emits a change event. |
| `.lazy` | Supported as an alias for `.change`. |

For a complete form, see [`wire:submit`](wire-submit.md). All bound values are
browser-controlled input. Keep secrets and permission decisions out of public
properties and validate values before persistence.

!!! info "Migrating from Magewire V1"
    V1's `wire:model` synchronized with the server by default. V3 defers a plain binding, and `.live` opts into
    immediate synchronization. `.lazy` remains an alias for `.change`; use `.blur` when focus loss is the intended
    trigger. See [Upgrade](../getting-started/upgrade.md).
