# Upgrade

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/upgrading") }}

This page covers upgrading from Magewire V1 to V3. It is meant to be read top-to-bottom the first time and used as a reference afterwards — copy the checklist at the end into a ticket or PR description when you start the work.

## TL;DR

1. Upgrade PHP, Magento, and Composer requirements.
2. Install V3: `composer require magewirephp/magewire:^3.0`.
3. Remove any separately-loaded Alpine.js from your theme.
4. Add `#[HandleBackwardsCompatibility]` to every existing component. The site should run as-is.
5. Migrate one component at a time using the checklist below.
6. Drop the BC attribute per component once it is fully V3-native.
7. Remove the BC feature registration when the whole module is migrated.

The BC layer is the key insight: V3 does not force you to migrate on day one. You can upgrade, keep shipping, and migrate at your own pace.

## Versioning

Magewire V2 never existed. Magewire V1 was built on Livewire V2, which created persistent version confusion — a "Magewire 1" that was effectively at Livewire's v2 feature line. V3 aligns Magewire's major version with Livewire's, so V2 was skipped entirely. Going forward, Magewire's major version tracks Livewire's.

## Requirements

Before running `composer update`, bring the surrounding environment up to spec.

- **Magento** `2.4.4` or later.
- **PHP** `8.2` or later.
- **Composer 2**.
- **No separately-loaded Alpine.js.** Magewire bundles the CSP build of Alpine inside its own JS bundle. Loading Alpine a second time clashes on directive registration and `$store` identity.

!!! warning "Remove Alpine from your theme first"
    Strip out any `<script src="…alpine.min.js">` tags from theme templates, layout XML, and bundle configs before installing V3. A double-Alpine page fails in confusing ways — silent Alpine expressions, lost reactivity, and console errors that do not obviously point at the root cause.

## Install the new version

```bash
composer require magewirephp/magewire:^3.0

bin/magento setup:upgrade
bin/magento setup:di:compile          # production mode only
bin/magento setup:static-content:deploy   # production mode only
bin/magento cache:flush
```

If you use the admin integration (new in V3), also install:

```bash
composer require magewirephp/magewire-admin
bin/magento module:enable Magewirephp_MagewireAdmin
bin/magento setup:upgrade
bin/magento cache:flush
```

In developer mode, skip the `di:compile` and `static-content:deploy` steps — Magento picks up the changes on the next request.

## Enable the backwards-compatibility layer

Magewire V3 ships a BC layer that lets V1 components keep running with minimal changes. Turn it on per component with the `#[HandleBackwardsCompatibility]` attribute:

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class LegacyCart extends \Magewirephp\Magewire\Component
{
    // Component code — no other changes required to keep V1 behaviour.
}

// Explicitly opt out — useful to override a theme-level auto-enable rule:
#[HandleBackwardsCompatibility(enabled: false)]
class ModernCart extends \Magewirephp\Magewire\Component { /* … */ }
```

The attribute lives in `Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility` — **not** under `Attributes\`. Getting the namespace right matters; a wrong `use` statement silently leaves the component on V3 defaults.

### What the BC layer does automatically

When BC is enabled for a component, at runtime Magewire:

- Rewrites `wire:model` → `wire:model.live`, `wire:model.defer` → `wire:model`, `wire:model.lazy` → `wire:model.blur`, `wire:model.delay.Xms` → `wire:model.live.debounce.Xms`.
- Returns a live-by-default proxy from `$wire.entangle('…')`.
- Re-triggers deprecated JS hook names (`component.initialized`, `element.updating`, `message.sent`, …) alongside their V3 replacements.
- Proxies `component.data` → `component.$wire` and `component.deferredActions` → `component.queuedUpdates`.
- Keeps `$this->id`, `$this->getPublicProperties()`, and the V1 `emit*()` family available on the base `Component` class via the `HandlesComponentBackwardsCompatibility` trait.

### What the BC layer does **not** do

You still have to manually handle:

- Component method signature changes (e.g. `updating($prop, $value)` parameter order).
- Public property type mismatches.
- Validation rule format changes.
- Behavioural changes in Magento or Hyvä that Magewire wraps.
- Any custom JS that listens directly on internal APIs that moved.

BC buys time; it does not eliminate migration work.

### The `memo.bc.enabled` flag

BC pivots on a single flag in the snapshot memo: `memo.bc.enabled`. When present and truthy, the BC shims activate for that component's DOM subtree. Otherwise they stay dormant — so unaffected components pay no runtime cost.

Resolution priority for the flag:

1. `#[HandleBackwardsCompatibility]` attribute (either `enabled: true` or `enabled: false`) — wins in all cases.
2. Programmatic assignment: `store($component)->set('magewire:bc', true)` from a Component Hook or Feature.
3. Theme default. Hyvä Checkout auto-enables BC for every component rendered inside the `hyva-checkout-main` container — see [Theming → Hyvä Checkout BC](../theming/hyva-checkout-bc.md).

## Breaking changes

Below is the exhaustive list. Each section identifies the V1 shape, the V3 shape, and what the BC layer does for you automatically.

### `wire:model` is deferred by default

| V1 | V3 | BC auto-handled? |
|---|---|---|
| `wire:model` | `wire:model.live` | Yes |
| `wire:model.defer` | `wire:model` | Yes |
| `wire:model.lazy` | `wire:model.blur` | Yes |
| `wire:model.delay.500ms` | `wire:model.live.debounce.500ms` | Yes |

V1's default was "sync on every keystroke", V3's default is "sync on form submit / next request". If you want instant sync in a V3 component, you must opt in with `.live`. The `.defer` / `.lazy` / `.delay` modifiers no longer exist in V3.

### Entangle is deferred by default

```html
<!-- V1: live by default -->
<div x-data="{ open: $wire.entangle('open') }">…</div>

<!-- V3: deferred by default. Add .live for instant sync. -->
<div x-data="{ open: $wire.entangle('open').live }">…</div>
```

BC auto-restores the V1 live-by-default proxy. Once the component is migrated, decide per `entangle` call whether you want live or deferred — each call site may want a different answer.

### Event listeners use the `#[On]` attribute

```php
use Magewirephp\Magewire\Attributes\On;

// V1
protected $listeners = ['cart-updated' => 'refresh'];
public function refresh(): void { /* … */ }

// V3
#[On('cart-updated')]
public function refresh(): void { /* … */ }
```

`$listeners` still works (the base `Component` class still reads it) but is discouraged. `#[On]` gives better IDE support and lets a single method respond to multiple events via multiple attributes.

Dispatch from PHP: `$this->dispatch('event-name', foo: 'bar')` — replaces V1's `$this->emit('event-name', ['foo' => 'bar'])`. The BC trait keeps `emit`, `emitUp`, `emitSelf`, and `emitTo` available, but they are thin wrappers around `dispatch()` now.

### Hook / event renames (JS)

| V1 name | V3 name | BC auto-handled? |
|---|---|---|
| `component.initialized` | `component.init` | Yes |
| `element.initialized` | `element.init` | Yes |
| `element.updating` | `morph.updating` | Yes |
| `element.removed` | `morph.removed` | Yes |
| `message.sent` | `commit` | Yes |
| `message.failed` | `commit` → `fail()` | Yes |
| `message.received` | `commit` → `succeed()` | Yes |
| `message.processed` | `commit` → `succeed()` → `queueMicrotask` | Yes |

The V3 `commit` hook is callback-based — the before half runs synchronously; the returned closure receives `succeed` / `fail` / `respond` continuations you can hook into. See [Component Hooks](../advanced/architecture/component-hooks.md) for the full signature.

### Component property aliases (JS)

| V1 | V3 | BC auto-handled? |
|---|---|---|
| `component.data` | `component.$wire` | Yes |
| `component.deferredActions` | `component.queuedUpdates` | Yes |

### PHP component API

| V1 | V3 | Status |
|---|---|---|
| `$this->emit('e', [...])` | `$this->dispatch('e', ...)` | V1 call kept under the BC trait; prefer `dispatch()`. |
| `$this->emitUp('e', ...)` | `$this->dispatch('e', ...)->up()` | V1 kept; prefer `->up()` chain. |
| `$this->emitSelf('e', ...)` | `$this->dispatch('e', ...)->self()` | V1 kept; prefer `->self()` chain. |
| `$this->emitTo('other', 'e', …)` | `$this->dispatch('e', ...)->to('other')` | V1 kept; prefer `->to()` chain. |
| `$this->dispatchBrowserEvent('e', …)` | `$this->js("window.dispatchEvent(new CustomEvent('e', { detail: … }))")` or a frontend `#[On]` handler | V1 kept under BC trait. |
| `$this->getPublicProperties()` | `$this->all()` | V1 kept under BC trait. |
| `public $this->id` | `$this->id()` / `$this->getId()` | Public property only exists in BC trait; removed from non-BC components. |

### Lifecycle hooks

V3 adds more lifecycle hooks than V1 exposed. All are optional:

| Hook | When it fires |
|---|---|
| `boot()` | Every request, before mount/hydrate. |
| `booted()` | Every request, after boot/hydrate sequence. |
| `initialize()` | Every request, before mount/hydrate. |
| `mount(array $params)` | Initial render only. |
| `hydrate()` | Every subsequent request. |
| `hydrateXxx()` | Hydrate for a specific property. |
| `updating($prop, $value)` | Before any property update. |
| `updatingXxx($value)` | Before a specific property updates. |
| `updated($prop, $value)` | After any property update. |
| `updatedXxx($value)` | After a specific property updates. |
| `rendering($view, $data)` | Before the template renders. |
| `rendered($view, $html)` | After the template renders. |
| `dehydrate()` | Before state is serialized back to snapshot. |
| `dehydrateXxx()` | Dehydrate for a specific property. |
| `exception(\Throwable $e, callable $stopPropagation)` | On exception. |

V1's `hydrate()` / `dehydrate()` signatures survive but V3 adds per-property variants and a `booted()` / `initialize()` pair — useful for DI wiring or authorisation guards.

### `updating` / `updated` argument order

V1 called `updatingFooBar($value)` with the new value as the only argument. V3 passes `updatingFooBar($value, $oldValue, ...)` in some cases. Check the `UpdatingUpdatedArgumentSwapResolver` BC rule if a V1 hook starts receiving the wrong arguments — it sits in `lib/MagewireBc/Features/SupportMagewireBackwardsCompatibility/Resolver/`.

### There is no `render()` method on `Component`

V1 examples occasionally showed a custom `render(): string` method to pick a template per state. V3 has no such method. The block's template renders automatically; to swap templates per state, use the `rendering` hook:

```php
public function rendering(): void
{
    $this->magewireBlock()->setTemplate(
        $this->state === 'review'
            ? 'Vendor_Module::magewire/review.phtml'
            : 'Vendor_Module::magewire/default.phtml'
    );
}
```

### Area-scoped DI is required

V1 registered Features, Mechanisms, and Hooks in the global `etc/di.xml`. V3's service provider reads area-scoped DI only — registrations in global DI are ignored.

Move every Magewire-related `<type>` block into `etc/frontend/di.xml` (and/or `etc/adminhtml/di.xml` if the registration should also apply in admin).

Registration targets:

```xml
<!-- Features / custom Component Hooks -->
<type name="Magewirephp\Magewire\Features">
    <arguments>
        <argument name="items" xsi:type="array">
            <item name="my_feature" xsi:type="array">
                <item name="type" xsi:type="string">Vendor\Module\Magewire\Features\MyFeature</item>
                <item name="sort_order" xsi:type="number">50000</item>
                <item name="boot_mode" xsi:type="number">30</item>
            </item>
        </argument>
    </arguments>
</type>

<!-- Synthesizers (HandleComponents mechanism) -->
<type name="Magewirephp\Magewire\Mechanisms\HandleComponents\HandleComponents">
    <arguments>
        <argument name="synthesizers" xsi:type="array">
            <item name="money" xsi:type="string">Vendor\Module\Magewire\Synthesizers\MoneySynth</item>
        </argument>
    </arguments>
</type>

<!-- Component resolvers -->
<type name="Magewirephp\Magewire\Mechanisms\ResolveComponents\Management\ComponentResolverManager">
    <arguments>
        <argument name="resolvers" xsi:type="array">
            <item name="my_resolver" xsi:type="object" sortOrder="90000">
                Vendor\Module\Mechanisms\ResolveComponents\ComponentResolver\MyResolver
            </item>
        </argument>
    </arguments>
</type>
```

### Features are Component Hooks now

V1's "Feature" convention was informal. V3 Features extend `Magewirephp\Magewire\ComponentHook` and expose a `provide()` method that subscribes to lifecycle events:

```php
use Magewirephp\Magewire\ComponentHook;
use Magewirephp\Magewire\Component;
use function Magewirephp\Magewire\on;

class SupportMyFeature extends ComponentHook
{
    public function provide(): void
    {
        on('render', function (Component $component) {
            return function (string $html) {
                // After-render transformation.
                return $html;
            };
        });
    }
}
```

If you registered a V1 "feature" as a plugin or observer, consider whether it should become a real Component Hook — the middleware semantics are usually cleaner.

### Synthesizers replace V1's hydrators

V1 had a `HydratorInterface`. V3 uses **Synthesizers** — classes that explain how to serialise and deserialise a given type across the snapshot boundary.

Magewire ships synthesizers for scalars, arrays, `\stdClass`, backed enums, and `\Magento\Framework\DataObject`. For custom value objects, write a `Synth` and register it:

```php
class MoneySynth extends \Magewirephp\Magewire\Mechanisms\HandleComponents\Synthesizers\Synth
{
    public static $key = 'mny';

    public static function match($target): bool
    {
        return $target instanceof \Vendor\Module\Model\Money;
    }

    public function dehydrate(Money $target, $dehydrateChild): array
    {
        return [['amount' => $target->amount(), 'currency' => $target->currency()], []];
    }

    public function hydrate($value, $meta, $hydrateChild): Money
    {
        return new Money($value['amount'], $value['currency']);
    }
}
```

Old `HydratorInterface` implementations survive under `lib/MagewireBc/Model/HydratorInterface.php` but are wrapped — convert to Synthesizers when you can.

### Alpine.js is bundled and CSP

V3 ships the CSP build of Alpine inside its JavaScript bundle. Two consequences:

- No second Alpine. Any `<script src="alpine.min.js">` in your theme must go.
- CSP-mode Alpine does not evaluate JavaScript expressions with `eval` / `new Function`. Arrow functions, template literals, destructuring, spread, and nested assignments inside Alpine *directive expressions* (`x-on:click="…"`, `x-init="…"`, etc.) are unavailable. Move complex logic into `Alpine.data()` registrations or a utility on `window.MagewireUtilities`.

Plain `<script>` tags in your PHTML still use normal JS — only the expressions that Alpine itself evaluates are affected.

### CSP fragments replace hand-rolled nonces

V1 templates sometimes carried hand-rolled CSP nonces or hashes on inline `<script>` tags. V3 offers **Fragments** — wrap any inline `<script>` in a fragment and Magewire injects the right nonce or hash automatically:

```php
<?php
$fragment = $block->getData('view_model')->utils()->fragment();
$script = $fragment->make()->script()->start();
?>
<script>console.log('Hello');</script>
<?php $script->end(); ?>
```

Strip your hand-rolled nonces when you migrate the template. See [Fragments](../concepts/fragments.md).

### Namespace changes

| V1 | V3 |
|---|---|
| `Magewirephp\Magewire\Attributes\HandleBackwardsCompatibility` *(never existed, common mis-import)* | `Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility` |
| `Livewire\Mechanisms\HandleComponents\Synthesizers\Synth` | `Magewirephp\Magewire\Mechanisms\HandleComponents\Synthesizers\Synth` |

The `On` attribute namespace did **not** change: `Magewirephp\Magewire\Attributes\On`.

## Migration workflow

Recommended sequence for a module that has more than a handful of V1 components. Treat each numbered step as a separate PR or commit — they are cleanest in isolation.

### 1. Install V3 with BC on everything

Add `#[HandleBackwardsCompatibility]` to every V1 component in the module. Run the test suite; visit the site. The goal here is not to change behaviour — the goal is to prove that BC alone keeps the site green.

### 2. Migrate wire directives

Find every `wire:model*` in templates and rewrite against the table above. Remove `.defer`, `.lazy`, `.delay`. Add `.live` where you need instant sync, `.blur` where you need on-blur, `.live.debounce.Xms` for debounced live.

```bash
grep -rn "wire:model" app/code your-theme/
```

### 3. Migrate entangle calls

Grep for `$wire.entangle(` and decide per call site whether you want `.live` (instant sync) or deferred (the V3 default).

```bash
grep -rn "entangle(" app/code your-theme/
```

### 4. Migrate `$listeners` arrays to `#[On]`

```bash
grep -rn "protected \$listeners" app/code
```

Each entry becomes an `#[On('event-name')]` attribute on the target method.

### 5. Migrate JS hook names

If your theme or custom JS listens on `message.sent`, `element.updating`, `component.initialized`, or friends, move those listeners to the V3 names (see the rename table above). The BC layer re-triggers the old names for BC-enabled components, but removing your dependency on the old names is the cleaner end state.

### 6. Migrate PHP component calls

- `$this->emit(…)` → `$this->dispatch(…)`.
- `$this->emitUp(…)` → `$this->dispatch(…)->up()`.
- `$this->emitTo('other', …)` → `$this->dispatch(…)->to('other')`.
- `$this->getPublicProperties()` → `$this->all()`.
- `$this->id` → `$this->id()` or `$this->getId()`.

### 7. Move DI registrations

Walk `etc/di.xml` for any `<type name="Magewirephp\Magewire\…">` blocks. Move them into `etc/frontend/di.xml` (and `etc/adminhtml/di.xml` if they should also run in admin). Anything Magewire-related in global `etc/di.xml` is ignored.

### 8. Drop the BC attribute per component

As each component becomes fully V3-native, switch its attribute to `#[HandleBackwardsCompatibility(enabled: false)]`. That component no longer pays the BC-shim runtime cost. When every component in the module is V3-native, remove the attribute entirely.

### 9. Remove the BC feature registration (whole-module)

When every component on the site is migrated (not just the ones in your module — any V1 component left on the site will break), remove the BC feature registration from your theme compatibility module's DI. The JS shim bundle stops loading.

## Hyvä Checkout

Hyvä Checkout V1 is wired for Livewire V2 semantics. Good news: the Hyvä theme module ships a BC layer that auto-enables `#[HandleBackwardsCompatibility]` for every component rendered inside the `hyva-checkout-main` layout container.

In practice that means an unchanged Hyvä Checkout V1 site runs on Magewire V3 without any manual BC opt-in. For most merchants, the checkout just keeps working after the upgrade.

If you customise Hyvä Checkout components, plan their migration with the main workflow above — the auto-enable rule only covers BC at runtime, not long-term migration.

See [Theming → Hyvä Checkout BC](../theming/hyva-checkout-bc.md) for the full detail.

## Admin (new in V3)

Magewire V1 was storefront-only. V3 supports admin components through the companion package `magewirephp/magewire-admin`. If the site has admin Magewire use cases — reactive grids, inline editors, wizards — install it alongside core. See [Admin → Installation](../admin/installation.md) and [Admin → How it works](../admin/how-it-works.md).

Admin components use the exact same layout-XML / PHTML / `$wire` conventions as storefront. The argument name in layout XML stays `magewire` (same as storefront). The `LayoutAdminResolver` picks up admin-area blocks automatically; you never reference `layout_admin` in your own XML.

## Common upgrade gotchas

A grab-bag of issues seen during real upgrades — hit this list before opening an issue.

- **"`wire:click` stopped working after upgrade"** — you probably still have a second Alpine loaded. Check the theme bundle and any layout XML that adds Alpine's script.
- **"Half my snapshots fail checksum validation"** — the Magento crypt key changed between the snapshot being issued and the request arriving. Flush FPC; force one page reload.
- **"CSP violations on every inline script"** — wrap inline scripts in a Script fragment. See the [CSP fragments](#csp-fragments-replace-hand-rolled-nonces) section.
- **"A V1 component I added `#[HandleBackwardsCompatibility]` to still behaves V3"** — the attribute import is most likely wrong. The correct namespace is `Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility`.
- **"`$this->emit` throws `BadMethodCallException`"** — the component does not use the BC trait (or it extends a class that removed it). Switch to `$this->dispatch()`.
- **"My observer listening on `message.sent` stopped firing"** — the JS-side hook is now `commit`. For server-side observer events see the table in [Features](../advanced/architecture/features.md#faq).
- **"My Feature's `provide()` is never called"** — the Feature is registered in the global `etc/di.xml`. Move it into `etc/frontend/di.xml` and/or `etc/adminhtml/di.xml`.
- **"Entangle spams the network tab"** — the call is still live-by-default from BC. Remove the `#[HandleBackwardsCompatibility]` attribute once the component is migrated, then audit every `entangle` on that component.

## Verifying the upgrade

After migrating, confirm the end state:

1. **No V1 directive lingers.**
   ```bash
   grep -rEn "wire:model(\.defer|\.lazy|\.delay)" app/code your-theme/
   ```
2. **No V1 hook name lingers.** Search JS for `message.sent`, `component.initialized`, `element.updating`, `element.removed`.
3. **No V1 PHP helper lingers.** Search for `->emit(`, `->emitUp(`, `->emitSelf(`, `->emitTo(`, `->dispatchBrowserEvent(`, `->getPublicProperties(`, `$this->id` accesses.
4. **No global Magewire DI remains.**
   ```bash
   grep -lrn "Magewirephp\\\\Magewire" app/code/**/etc/di.xml
   ```
   Anything matching must move to `etc/frontend/di.xml` or `etc/adminhtml/di.xml`.
5. **No component still carries `#[HandleBackwardsCompatibility]`** — once fully migrated. A repo-wide grep proves the migration is complete.
6. **Site health.** Click through the top ten most-trafficked Magewire components, watching the browser devtools Network tab for 4xx/5xx on `/magewire/update` and the console for CSP violations or Alpine warnings.

## Rolling back

If the upgrade surfaces a showstopper bug, you can roll back to V1 by restoring the previous `composer.lock`, running `composer install`, and flushing caches. Any V3-specific code (the `#[HandleBackwardsCompatibility]` attribute, `->dispatch()->to()` chains, `#[On]` attributes) will need to be reverted first — V1 will not understand them. Keep the migration PR small enough that the revert is reasonable.

## Migration checklist

Copy this into a PR description.

- [ ] PHP is on 8.2+, Magento on 2.4.4+.
- [ ] Composer updated to `magewirephp/magewire:^3.0`.
- [ ] `magewirephp/magewire-admin` installed if the site uses Magewire in admin.
- [ ] Every separately-loaded Alpine.js removed from theme templates and bundle configs.
- [ ] Every existing component carries `#[HandleBackwardsCompatibility]` (imported from `Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\`).
- [ ] `wire:model.defer` → `wire:model`.
- [ ] `wire:model.lazy` → `wire:model.blur`.
- [ ] Bare `wire:model` → `wire:model.live` where instant sync is required.
- [ ] `wire:model.delay.Xms` → `wire:model.live.debounce.Xms`.
- [ ] Every `$wire.entangle('…')` audited — `.live` added where needed.
- [ ] Every `protected $listeners = […]` replaced with `#[On('event-name')]` attributes.
- [ ] Every `$this->emit*()` migrated to `$this->dispatch()` (with `->up()`, `->self()`, `->to()` as appropriate).
- [ ] Every `$this->getPublicProperties()` migrated to `$this->all()`.
- [ ] Every `$this->id` access migrated to `$this->id()` / `$this->getId()`.
- [ ] Every deprecated JS hook name (`message.sent`, `component.initialized`, `element.updating`, `element.removed`) migrated to the V3 name.
- [ ] Every `component.data` / `component.deferredActions` JS access migrated to `component.$wire` / `component.queuedUpdates`.
- [ ] Every Feature / Mechanism / Hook / Synthesizer / Resolver registration moved from global `etc/di.xml` to `etc/frontend/di.xml` (and `etc/adminhtml/di.xml` as needed).
- [ ] Inline `<script>` tags wrapped in Script fragments where CSP compliance matters.
- [ ] Custom `HydratorInterface` implementations rewritten as Synthesizers.
- [ ] `render(): string` methods replaced by `rendering()` hooks that call `magewireBlock()->setTemplate(...)`.
- [ ] BC attribute set to `enabled: false` (or removed) on fully migrated components.
- [ ] Smoke-tested against the top-trafficked components (devtools Network + console).

Migration done. You can now remove the theme BC feature registration when every module on the site has reached this state.

## Related

- [Backwards compatibility](../theming/backwards-compatibility.md) — the BC system in depth.
- [Hyvä Checkout BC](../theming/hyva-checkout-bc.md) — the auto-enable rule.
- [Admin → Installation](../admin/installation.md) — install the admin companion package.
- [Features](../advanced/architecture/features.md) — how to rewrite V1 Features as V3 Component Hooks.
- [Synthesizers](../advanced/synthesizers.md) — replacement for V1 hydrators.
