# Alpine

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/offline") }}

## Single Alpine bundle

Magewire ships Alpine.js bundled into its own JavaScript build. Do **not** load a second Alpine — two Alpine instances clash on directive registration and `$store` identity.

## CSP build

The bundled build is the CSP variant: it evaluates directive expressions without `eval` / `new Function`. Arrow functions, template literals, destructuring, spread, globals, and nested assignments inside Alpine attributes are unavailable. Move logic into `Alpine.data()` or a utility on `window.MagewireUtilities`.

## Init events

| Event | Register |
|---|---|
| `alpine:init` | `Alpine.data()`, `Alpine.store()`, `Alpine.bind()`, utilities |
| `magewire:init` | `Magewire.hook()` — commit, request, morph hooks |
| `magewire:initialized` | `Magewire.directive()` — custom `mage:*` directives |

Always pass `{ once: true }` — Magewire may re-fire init events across SPA navigations.

## Registering through layout containers

Add Alpine `x-data` registrations as blocks inside Magewire's named containers:

```xml title="view/frontend/layout/default.xml"
<referenceContainer name="magewire.alpinejs.components">
    <block name="magewire.alpinejs.components.search-box"
           template="Vendor_Module::js/alpinejs/components/search-box.phtml" />
</referenceContainer>
```

Inside the phtml, emit the script via a [fragment](../concepts/fragments.md) to stay CSP-compliant:

```html title="view/frontend/templates/js/alpinejs/components/search-box.phtml"
<?php
$magewireViewModel = $block->getData('view_model');
$fragment = $magewireViewModel->utils()->fragment();
$script = $fragment->make()->script()->start();
?>
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('searchBox', () => ({ query: '' }));
    }, { once: true });
</script>
<?php $script->end(); ?>
```
