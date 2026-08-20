# Events

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/events") }}

Component events use Livewire 3's `dispatch()` and `#[On]` concepts. Use them for application communication between components and browser code.

```php
use Magewirephp\Magewire\Attributes\On;

$this->dispatch('cart-updated', count: $this->itemCount);

#[On('cart-updated')]
public function refreshSummary(int $count): void
{
    // …
}
```

The V1 `emit*()` methods and `$listeners` property are migration APIs provided by the [backwards-compatibility layer](backwards-compatibility.md). New Magewire 3 components should use `dispatch()` and attributes.

## Framework hooks are different

Magewire also has an internal `on()` / `trigger()` pipeline used by mechanisms and features. Those hooks are framework extension points, not component-dispatched events.

```php
use function Magewirephp\Magewire\on;

on('render', function ($component, $view, $data) {
    // Before render.

    return function ($html) {
        // After render.
        return $html;
    };
});
```

The current observable internal map includes:

- Magewire lifecycle: `magewire:component:construct`, `magewire:component:reconstruct`, `magewire:component:build`, `magewire:view:compile`, `magewire:setup`, and `magewire:boot`;
- component lifecycle: `pre-mount`, `mount.stub`, `mount`, `hydrate`, `update`, `call`, `render`, `render.placeholder`, `dehydrate`, and `destroy`;
- Magento rendering: `magento:block:render`, `magento:block:rendered`, and `magento:template:render`;
- transport and integrity: `request`, `response`, `checksum.generate`, `checksum.verify`, `checksum.fail`, and `snapshot-verified`;
- utility hooks: `__get`, `__unset`, `__call`, `exception`, `flush-state`, and `profile`.

Not every internal event has the same arguments or return pipeline. Inspect the tagged call site before writing a low-level hook.

## Magento observers

The observer bridge re-emits its explicit internal event map as Magento events. Non-alphanumeric characters become underscores:

```text
magewire:component:construct → magewire_on_magewire_component_construct
checksum.fail               → magewire_on_checksum_fail
render                      → magewire_on_render
```

See [Magento Observer Events](../advanced/architecture/observer-events.md) for registration and before/after callback semantics.
