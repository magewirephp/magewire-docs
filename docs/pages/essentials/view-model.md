# View Model & Utilities

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Most templates need the same handful of helpers — a CSRF token, a CSP nonce, an environment check,
a fragment builder. Rather than make you write a custom ViewModel for each, Magewire ships one
`MagewireViewModel` and exposes a growing set of **utilities** through it.

## How it gets there

The `SupportMagewireViewModel` feature listens for block rendering and **auto-binds** a
`MagewireViewModel` as the `view_model` argument on the root `magewire` block and every block beneath
it — unless you've already set a `view_model` of your own. You don't wire anything up.

So in any `.phtml` rendered inside the Magewire tree:

```php
/** @var \Magewirephp\Magewire\Features\SupportMagewireViewModel\MagewireViewModelInterface $viewModel */
$viewModel = $block->getData('view_model');
```

And from inside a component class:

```php
$viewModel = $this->magewireViewModel();
```

!!! info "Why a bound view model, not a global `$magewireViewModel`?"
    Binding it as a block argument means a block keeps working even when it's moved out of the
    `magewire` wrapper — no template changes needed. A global template variable wouldn't survive that
    move. If you set your own `view_model`, it must implement `MagewireViewModelInterface`.

## The `utils()` entry point

Everything hangs off `utils()`:

```php
$viewModel->utils();              // the Utils aggregator
$viewModel->utils()->security();  // a specific utility
```

| Utility | Accessor | Purpose |
|---|---|---|
| **Magewire** | `utils()->magewire()` | Runtime, config, update URI, the mechanisms/features registries. |
| **Security** | `utils()->security()` | CSRF token access. |
| **Environment** | `utils()->env()` | Developer / production mode checks. |
| **CSP** | `utils()->csp()` | Content-Security-Policy nonce generation. |
| **Fragment** | `utils()->fragment()` | Build template fragments — see [Fragments](../concepts/fragments.md). |
| **Layout** | `utils()->layout()` | Containerize and render child blocks. |
| **Template** | `utils()->template()` | Template-compilation helpers. |
| **Alpine** | `utils()->alpinejs()` | Alpine.js integration — extension point. |
| **Tailwind** | `utils()->tailwind()` | Tailwind helpers — extension point. |
| **Application** | `utils()->application()` | Application-level helpers — extension point. |

!!! note
    `alpinejs()`, `tailwind()` and `application()` are reserved extension points — they exist so the
    surface is stable, but carry no methods of their own yet. The utilities below are the ones with
    behaviour today.

## Magewire — `utils()->magewire()`

Access to the Magewire runtime and configuration:

| Method | Returns |
|---|---|
| `config()` | The Magewire system configuration object. |
| `getUpdateUri()` | The `/magewire/update` endpoint URL. |
| `logger()` | The PSR logger. |
| `canRequireMagewireJsLibrary()` | Whether the JS library still needs to be required on this page. |
| `mechanisms()` | The mechanisms registry helper. |
| `features()` | The features registry helper. |
| `build()` | The Magewire `Builder`. |

```php
<?php $magewire = $viewModel->utils()->magewire(); ?>
<script>window.MAGEWIRE_UPDATE_URI = '<?= $magewire->getUpdateUri() ?>';</script>
```

## Security — `utils()->security()`

```php
$token = $viewModel->utils()->security()->getCsrfToken();
```

Returns Magento's form key, the CSRF token every Magewire request is validated against.

## Environment — `utils()->env()`

```php
if ($viewModel->utils()->env()->isDeveloperMode()) {
    // Verbose, dev-only output.
}

$viewModel->utils()->env()->isProductionMode();
```

## CSP — `utils()->csp()`

Generate Content-Security-Policy nonces for inline scripts and styles:

```php
$csp = $viewModel->utils()->csp();

$nonce = $csp->generateNonce();                 // raw nonce value
$attr  = $csp->generateNonceAttribute();        // e.g. ` nonce="..."` (note the leading space)
$attr  = $csp->generateNonceAttribute('%s');    // without the leading space
```

```php
<script<?= $viewModel->utils()->csp()->generateNonceAttribute() ?>>
    /* CSP-compliant inline script */
</script>
```

## Fragment — `utils()->fragment()`

Builds template fragments — marked regions whose output can be modified (for example, to make inline
scripts CSP-compliant):

```php
$fragment = $viewModel->utils()->fragment()->make();          // default factory
$fragment = $viewModel->utils()->fragment()->make('my-type'); // a registered custom type
```

See [Fragments](../concepts/fragments.md) for the full `start()` / `end()` workflow and registering
custom fragment types.

## Layout — `utils()->layout()`

Helpers for working with child blocks and rendering blocks as containers:

| Method | Purpose |
|---|---|
| `getChild($block, $alias, $data = [])` | Fetch a named child block. |
| `getChildHtml($block, $alias, $data = [])` | Render a named child block to HTML. |
| `canContainerizeBlock($block)` | Whether a block can be rendered as a container. |
| `containerizeBlock($block)` | Wrap a block as a container structure. |
| `renderBlockAsContainer($block)` | Render a block as a container. |

## Adding your own utility

The utilities collection is extensible. Register a custom utility (implementing `UtilsInterface`) via
DI, then reach it by name through `utils()`:

```php
$viewModel->utils('myUtility');
```

This keeps project-specific template helpers in one predictable place instead of scattered custom
ViewModels.

## Related

- [Components](components.md) — where `$magewire` and `view_model` come from.
- [Fragments](../concepts/fragments.md) — the fragment builder in depth.
- [Notables](../getting-started/notables.md) — the automatic `view_model` resolution rule.