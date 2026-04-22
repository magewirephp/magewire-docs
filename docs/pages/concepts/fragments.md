# Fragments

!!! tip "Fragments can also be used outside Magewire components!"

A **Fragment** is an explicitly-scoped slice of output — a region of a template or a string of rendered HTML — that Magewire can validate, enhance, and transform before it reaches the browser. Fragments are the plumbing behind Magewire's CSP support, developer-mode annotations, Flakes, and any other feature that needs a second pass over inline markup.

Think of a fragment as a typed buffer: you tell Magewire *what kind of output this is* (a `<script>`, a `<style>`, arbitrary HTML, a JS literal), and Magewire runs the registered validators and modifiers for that type.

## Why fragments exist

PHTML templates in Magento are plain output — whatever you `echo` lands in the HTTP response as-is. That means every inline `<script>` is a CSP pain point, every `<style>` bypasses your theme's asset pipeline, and every bit of rendered HTML is opaque to tooling.

Fragments flip that. When the contents of an `echo` pass through a fragment, the framework gets a chance to:

- **Validate** the shape (e.g. a `script` fragment must start with `<script` and end with `</script>`).
- **Decorate** the root element (attributes, nonces, data-flags).
- **Register with other subsystems** (dynamic CSP collector, FPC hash list, Magewire slots).
- **Swap rendering strategy** by environment (developer mode adds a debug attribute; production doesn't).

The template author writes normal-looking markup; the framework makes it safe, observable, and policy-compliant.

## The smallest example

```html
<?php
$fragment = $block->getData('view_model')->utils()->fragment();
?>

<?php $script = $fragment->make()->script()->start() ?>
<script>
    console.log('Custom Fragment');
</script>
<?php $script->end() ?>
```

- `utils()->fragment()` resolves the `Fragment` utility from the Magewire ViewModel.
- `->make()` returns the `FragmentFactory`.
- `->script()` instantiates a `Script` fragment.
- `->start()` opens an output buffer; `->end()` closes it, runs validators and modifiers, and echoes the result.

On a cached page, the Csp modifier hashes the inline JS and registers the hash in the dynamic CSP collection. On an uncached request, it injects a `nonce="..."` attribute instead. The template author never has to think about any of that.

## Built-in fragment types

Available on `FragmentFactory` (and therefore on `$viewModel->utils()->fragment()->make()`):

| Method | Class | Intended use |
|---|---|---|
| `html()` | `Fragment\Html` | Generic HTML with root-element attribute decoration. |
| `script()` | `Fragment\Script` | Inline `<script>` tag — validated start/end, CSP-aware. |
| `style()` | `Fragment\Style` | Inline `<style>` tag. |
| `javascript()` | `Fragment\Javascript` | A raw JavaScript literal (not wrapped in `<script>`). |
| `component($block)` | `Fragment\Component` | Wraps a Magewire component's rendered root for morph-safe boundaries. |
| `custom('name')` | registered via DI | Typed fragment for feature-specific output (Flakes use this). |

### HTML fragment — decorating a rendered block

```html
<?php $html = $fragment->make()->html()->withAttribute('data-trackable', 'cart-row')->start() ?>
<div class="cart-row">
    <?= $escaper->escapeHtml($magewire->title) ?>
</div>
<?php $html->end() ?>
```

`withAttribute` merges attributes into the root element at render time — no string concatenation required. Multiple calls accumulate; `withAttributes([...])` sets a batch at once.

### Style fragment

```html
<?php $style = $fragment->make()->style()->start() ?>
<style>
    .cart-row { border: 1px solid var(--magewire-border, #ccc); }
</style>
<?php $style->end() ?>
```

### Wrapping pre-rendered HTML

Sometimes the HTML already exists as a string (rendered elsewhere, fetched from a service, stored in a model). `start`/`end` buffering doesn't help here — use `wrap` instead:

```php title="Vendor\Module\Model\View\Renderer"
<?php

namespace Vendor\Module\Model\View;

use Magewirephp\Magewire\Model\View\FragmentFactory;

class Renderer
{
    public function __construct(
        private readonly FragmentFactory $fragmentFactory
    ) {
    }

    public function render(string $html): string
    {
        return $this->fragmentFactory->html()->wrap($html);
    }
}
```

`wrap` does `start → render → end` in one call. Modifiers and validators run exactly like in the buffered flow.

## The Script fragment

The `Script` fragment is worth studying because it shows how validation and modification layer on top of the base `Fragment`. The class itself is tiny:

```php title="Magewirephp\Magewire\Model\View\Fragment\Script"
class Script extends \Magewirephp\Magewire\Model\View\Fragment\Html
{
    public function start(): static
    {
        return parent::start()
            ->withValidator(static fn ($script) => str_starts_with($script, '<script'))
            ->withValidator(static fn ($script) => str_ends_with($script, '</script>'));
    }

    /**
     * Returns the content between the script tags.
     */
    public function getScriptCode(): string
    {
        // ...
    }
}
```

Two things happen:

1. **Validators** reject anything that isn't a well-formed `<script>…</script>` block. A typo or stray echo becomes a logged exception instead of mangled markup.
2. **`getScriptCode()`** gives modifiers access to *just the inline code* — useful for hashing (CSP) or linting.

Because `Script` extends `Html`, it inherits `withAttribute` / `withAttributes` — so a modifier can drop a `nonce="..."` onto the root `<script>` tag without rewriting the output string.

## Fragment Modifiers

A **Modifier** is a small class that mutates a fragment right before it renders. Modifiers are the extension point: CSP, developer-mode annotations, FPC integration, analytics tags — all live as modifiers.

Modifiers extend `Magewirephp\Magewire\Model\View\FragmentModifier`:

```php title="Magewirephp\Magewire\Model\View\Fragment\Modifier\Csp"
<?php

use Magewirephp\Magewire\Model\View\Fragment;

class Csp extends \Magewirephp\Magewire\Model\View\FragmentModifier
{
    public function modify(Fragment $fragment): Fragment
    {
        if (! $fragment instanceof Fragment\Script) {
            return $fragment;
        }

        // Hash the inline code → add to dynamic CSP collection (FPC page)
        // OR
        // Inject nonce="..." attribute → via $fragment->withAttribute('nonce', $nonce)

        return $fragment;
    }
}
```

Two rules worth internalising:

- **Type-check first.** Modifiers are registered per fragment class, but they often only care about a subset of shapes (e.g. the CSP modifier only touches `Script` fragments). An early `instanceof` guard keeps the logic readable.
- **Return the fragment.** Modifiers mutate in place (via `withAttribute`, etc.) and return the instance. Do not return a string — the pipeline expects a `Fragment`.

### Registering a modifier

Register modifiers on the target fragment class in `di.xml`. Sort order matters — modifiers run in ascending order, so hashing (needs final output) runs late, while annotation (safe to run anytime) runs early:

```xml
<type name="Magewirephp\Magewire\Model\View\Fragment\Script">
    <arguments>
        <argument name="modifiers" xsi:type="array">
            <item name="developer" sortOrder="500" xsi:type="object">
                Magewirephp\Magewire\Model\View\Fragment\Modifier\Developer
            </item>
            <!-- Maximum sort order to make sure this modifier is run last. -->
            <item name="csp" sortOrder="9900" xsi:type="object">
                Magewirephp\Magewire\Model\View\Fragment\Modifier\Csp
            </item>
        </argument>
    </arguments>
</type>
```

Register in `etc/frontend/di.xml` for storefront or `etc/adminhtml/di.xml` for admin — area-scope the modifier to the contexts where it should apply.

### Built-in modifiers worth knowing

| Modifier | Fragment | Effect |
|---|---|---|
| `Csp` | `Script` | Adds a hash to the dynamic CSP collector on cached pages; injects a nonce on uncached requests. |
| `Developer` | `Html` (and subclasses) | Adds a `magewire-fragment` boolean attribute to the root element when `MAGE_MODE=developer` — makes fragments visible in browser devtools. |

### A sketch of a custom modifier

A modifier that stamps every rendered Magewire script with the build hash for cache-busting in monitoring tools:

```php title="Vendor\Module\Model\View\Fragment\Modifier\StampBuild.php"
<?php

namespace Vendor\Module\Model\View\Fragment\Modifier;

use Magewirephp\Magewire\Model\View\Fragment;
use Magewirephp\Magewire\Model\View\FragmentModifier;
use Vendor\Module\Service\BuildInfo;

class StampBuild extends FragmentModifier
{
    public function __construct(
        private readonly BuildInfo $buildInfo
    ) {
    }

    public function modify(Fragment $fragment): Fragment
    {
        if ($fragment instanceof Fragment\Script) {
            $fragment->withAttribute('data-build', $this->buildInfo->sha());
        }

        return $fragment;
    }
}
```

Register it on `Magewirephp\Magewire\Model\View\Fragment\Script` with a sort order below `9900` so CSP still runs last.

## Custom fragment types

The `FragmentFactory` supports user-registered types. This is how `SupportMagewireFlakes` introduces a `flake` fragment without touching core:

```xml
<type name="Magewirephp\Magewire\Model\View\FragmentFactory">
    <arguments>
        <argument name="types" xsi:type="array">
            <item name="flake" xsi:type="string">
                Magewirephp\Magewire\Features\SupportMagewireFlakes\View\Fragment\FlakeFragment
            </item>
        </argument>
    </arguments>
</type>
```

In a template:

```php
<?php $flake = $viewModel->utils()->fragment()->make('flake')->start() ?>
    <!-- flake markup -->
<?php $flake->end() ?>
```

Your class must extend `Magewirephp\Magewire\Model\View\Fragment` (or `Fragment\Html` for attribute support). Add validators in `start()`, expose typed getters for modifiers to read, and register per-type modifiers via the same DI shape shown above.

## The Fragment lifecycle

Understanding the order of operations makes debugging much easier:

```
start()                         → opens ob_start(), records the buffer level
  │
  │ (developer writes markup)
  │
end()
  ├─ ob_get_clean()             → captures raw output into $this->raw
  ├─ validate()                 → runs every withValidator callback (exceptions logged, output suppressed)
  ├─ modify()                   → runs every registered FragmentModifier + callable in sort order
  │    └─ Html::render()        → merges accumulated withAttribute() values into root element
  └─ echo                       → writes the final output to the response (unless mute()'d)
```

A few knobs worth knowing:

- **`lock()`** — freeze a fragment so later code cannot mutate it (useful for shared/injected fragments).
- **`mute()`** — run the pipeline but suppress the echo. Hand the instance off to other code via `getRawOutput()` or `getScriptCode()`.
- **`withTag('name')`** — tag the fragment so a later pass can identify it by name.

## When to reach for a fragment

Good candidates:

- Inline `<script>` or `<style>` that needs CSP compliance without hand-rolled nonces.
- Any rendered region you want to annotate in developer mode (devtools-friendly data attributes, profiling hooks).
- A region whose final markup depends on something you cannot know until after render (an FPC-cached vs uncached branch, a nonce from the page config, a hash computed from output).
- A feature that needs to hand rendered HTML to another subsystem (Flakes → compiler, slots → layout tree).

When a plain `echo` is fine:

- Static template output that is not security-sensitive and needs no post-processing.
- Markup already emitted by a well-behaved block with its own output pipeline.

## Related

- [Magewire Flakes](../features/magewire-flakes.md) — a feature built entirely on top of custom fragment types.
- [Security](../advanced/security.md) — why the CSP modifier exists.
