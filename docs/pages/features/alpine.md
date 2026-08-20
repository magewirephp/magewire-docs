# Alpine

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/alpine") }}

## Single Alpine bundle

Magewire ships Alpine.js in its browser build. Two independently started Alpine instances clash on directive registration and `$store` identity, so asset coordination belongs to the theme compatibility package.

The maintained Hyvä package wraps Hyvä's Alpine block: a page containing Magewire components uses Magewire's bundled Alpine, while a page without them can fall back to Hyvä's copy. Do not remove or override the theme's Alpine assets globally; follow the integration package's layout strategy.

## CSP build

The bundled build is the CSP variant: it evaluates directive expressions without `eval` / `new Function`. Arrow functions, template literals, destructuring, spread, globals, and nested assignments inside Alpine attributes are unavailable. Move logic into `Alpine.data()` or a utility on `window.MagewireUtilities`.

## Init events

| Event | Register |
|---|---|
| `alpine:init` | `Alpine.data()`, `Alpine.store()`, `Alpine.bind()`, utilities |
| `magewire:init` | `Magewire.hook()` — commit, request, morph hooks |
| `magewire:initialized` | `Magewire.directive()` — custom `mage:*` directives |

Use `{ once: true }` for one-time global registrations.

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
