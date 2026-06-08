# Redirects

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/redirecting") }}

A component action can send the browser to another URL by calling `$this->redirect()`. The redirect
happens after the action finishes — it's queued as an effect on the response and performed by the JS
runtime, so it works the same whether triggered on an initial render or a `wire:click` update.

## Redirecting from an action

```php
use Magewirephp\Magewire\Component;

class SaveAddress extends Component
{
    public function save(): void
    {
        // … persist the address …

        $this->redirect('/checkout/payment');
    }
}
```

Pass any URL string. To build a Magento URL, resolve it the usual way (e.g. a `UrlInterface`
dependency on your component) and hand the result to `redirect()`:

```php
$this->redirect($this->urlBuilder->getUrl('checkout/cart'));
```

## What happens under the hood

`redirect()` is provided by the `SupportRedirects` feature. It:

1. Stores the target URL on the component's data store.
2. On `dehydrate`, adds a `redirect` effect to the component's snapshot.
3. **Skips the re-render** by default — there's no point rendering a component you're navigating away
   from. (Controlled by the `livewire.render_on_redirect` config; off by default.)

The browser receives the `redirect` effect and performs the navigation.

!!! note "The `$navigate` argument"
    `redirect()` accepts a second `$navigate` argument that opts into SPA-style navigation. That
    pathway is **not ready for use in Magewire yet** — call `redirect()` with a URL only, and let the
    browser perform a normal full navigation.

## Related

- [Actions](../essentials/actions.md) — where redirects are typically triggered.
- [Lifecycle Hooks](../essentials/lifecycle-hooks.md) — `dehydrate`, where the redirect effect is added.