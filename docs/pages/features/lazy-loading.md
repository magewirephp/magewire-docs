# Lazy Loading

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/lazy") }}

Lazy loading lets a component paint a lightweight **placeholder** on the initial
page load and fetch its real content on a follow-up XHR — either immediately, or
once the component scrolls into view. Use it to keep expensive components off the
critical render path.

## Opting in

Unlike Livewire, Magewire has no routing layer to mark a component lazy, so lazy
loading is opted into in one of two ways.

### The `#[Lazy]` attribute

{{ include("admonition/magewire-specific.md", since_version="3.4.0") }}

```php
use Magewirephp\Magewire\Attributes\Lazy;
use Magewirephp\Magewire\Component;

#[Lazy]
class ProductReviews extends Component
{
    // ...
}
```

### The `magewire:component:lazy` layout argument

Opt a component in (or force it off) from layout XML, without touching the class:

```xml
<block name="product.reviews" template="Vendor_Module::product/reviews.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object" shared="false">
            Vendor\Module\Magewire\ProductReviews
        </argument>
        <!-- "true" | "on-load" enables lazy loading; "false" disables it -->
        <argument name="magewire:component:lazy" xsi:type="string">on-load</argument>
    </arguments>
</block>
```

The layout argument wins over the attribute: `magewire:component:lazy="false"`
disables lazy loading even on a component carrying `#[Lazy]`.

## Trigger modes

| Value | Trigger |
|---|---|
| `on-intersect` *(default)* | Loads when the placeholder scrolls into the viewport. This is the default for `#[Lazy]` and for `magewire:component:lazy="true"`. |
| `on-load` | Loads immediately after the initial paint. Set via `magewire:component:lazy="on-load"`. |

## Placeholders

Define what shows before the real content by adding a `placeholder()` method to
the component. It may return either a **Magento template id** or a **raw HTML
string**.

{{ include("admonition/magewire-specific.md", since_version="3.4.0") }}

```php
class ProductReviews extends Component
{
    // A Magento template id — rendered as a standalone block.
    public function placeholder(array $params = []): string
    {
        return 'Vendor_Module::product/reviews-placeholder.phtml';
    }
}
```

```php
    // …or raw HTML returned directly.
    public function placeholder(array $params = []): string
    {
        return '<div><span class="animate-pulse">Loading reviews…</span></div>';
    }
```

!!! warning "Single root element"
    Placeholder markup must have a **single root element**. The lazy trigger and
    the component's `wire:id` are attached to that root. A template id is
    detected by the `Vendor_Module::path/to/file.phtml` pattern; anything else
    is treated as raw HTML. When `placeholder()` is absent or returns an empty
    string, Magewire falls back to `<div></div>`.

## Isolation

By default each lazy component loads in its own isolated request. Set
`isolate: false` to let a component's lazy request bundle together with other
non-isolated lazy requests on the same page — one XHR instead of several.

```php
#[Lazy(isolate: false)]
class ProductReviews extends Component
{
    // ...
}
```

See [Request Bundling](request-bundling.md) for how lazy requests pool.

## `mount()` runs on the lazy request

When a component is lazy, its `mount()` lifecycle hook does **not** run on the
initial (placeholder) paint — it runs on the follow-up lazy request, right
before the real content renders.

{{ include("admonition/magewire-specific.md", since_version="3.4.0") }}

Mount arguments are **not** ferried through the client. On the lazy request the
block is rebuilt from its layout handles, so its `mount()` arguments are
re-derived server-side. This keeps the client from being trusted with mount
input and means lazy components behave identically whether or not JavaScript
tampered with the placeholder.

## CSP compatibility

{{ include("admonition/magewire-specific.md", since_version="3.4.0") }}

The lazy trigger is a CSP-safe Alpine component (`magewireLazyLoad`) attached to
the placeholder root via `x-data`, rather than an inline `$wire.__lazyLoad()`
attribute expression. Hyvä's CSP-friendly Alpine build cannot evaluate a method
call inside an attribute, so lazy loading works under a strict Content-Security
-Policy out of the box — no `unsafe-eval` required.
