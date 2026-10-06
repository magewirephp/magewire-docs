# Upgrade

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/upgrading") }}

This page covers upgrading from Magewire V1 to V3. For upgrades between V3 releases, such as 3.6 to 3.7, see
[Upgrade notes](releases/upgrade-notes.md). Read this page top-to-bottom the first time, then use it as a reference. Copy the checklist at the end into a ticket or PR description when you start the work.

## TL;DR

1. Upgrade PHP, Magento, and Composer requirements.
2. Install V3: `composer require magewirephp/magewire:^3.7.2`.
3. Install or update the appropriate theme compatibility package so Alpine is loaded once.
4. Add `#[HandleBackwardsCompatibility]` to legacy components, then test each interaction. The layer covers specific
   V1 behaviors, and its directive rewrites currently run only on the Hyvä Checkout page. It is not a guarantee that
   unchanged component code will work.
5. Migrate one component at a time using the checklist below.
6. Drop the BC attribute per component once it is fully V3-native.
7. Remove obsolete BC attributes and any companion package installed only for legacy compatibility.

The BC layer is the key insight: V3 does not force you to migrate on day one. You can upgrade, keep shipping, and migrate at your own pace.

## Versioning

Magewire V2 never existed. Magewire V1 was built on Livewire V2, which created persistent version confusion: a "Magewire 1" that was effectively at Livewire's v2 feature line. V3 aligns Magewire's major version with Livewire's, so V2 was skipped entirely. Going forward, Magewire's major version tracks Livewire's.

See [Versioning](versioning.md) for the full versioning scheme, including how subpackages are tagged.

## Requirements

Before running `composer update`, bring the surrounding environment up to spec.

- **Magento or Mage-OS** on a release line supported by the selected Magewire tag. Magewire 3.7's tested floor is Magento Open Source 2.4.6-p15 or Mage-OS 1.3.1.
- **PHP** `8.2` or later.
- **Composer 2**.
- **A compatible theme integration.** Magewire bundles Alpine, while the compatibility package coordinates it with the theme's own loader.

!!! warning "Do not remove theme assets globally"
    A double-Alpine page fails in confusing ways, but removing a theme's loader globally can break pages without Magewire. For Hyvä, install `magewirephp/magewire-hyva-theme` and let it select the correct loader per page.

## Install the new version

```bash
composer require magewirephp/magewire:^3.7.2

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

In developer mode, skip the `di:compile` and `static-content:deploy` steps; Magento picks up the changes on the next request.

## Enable the backwards-compatibility layer

Magewire V3 ships a BC layer for specific V1 browser behaviors while components are migrated. It does not guarantee
that an unchanged V1 component will work. Turn it on per component with the
`#[HandleBackwardsCompatibility]` attribute, then test the complete interaction:

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class LegacyCart extends \Magewirephp\Magewire\Component
{
    // The documented BC transformations are enabled for this component.
}

// Explicitly opt out: required for V3-native components inside the Hyvä Checkout container:
#[HandleBackwardsCompatibility(enabled: false)]
class ModernCart extends \Magewirephp\Magewire\Component { /* … */ }
```

The attribute lives in `Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility`, **not** under `Attributes\`. Getting the namespace right matters; a wrong `use` statement silently leaves the component on V3 defaults.

### What the BC layer does automatically

When BC is enabled for a component, Magewire's PHP side:

- Adapts the selected V1 `updating*` and `updated*` hook argument shapes covered by its registered resolvers.
- Keeps `$this->id`, `$this->getPublicProperties()`, and the V1 `emit*()` family available on the base `Component` class via the `HandlesComponentBackwardsCompatibility` trait. These are present on every component, with or without BC.

The browser-side rewrites come from a companion package. On the Hyvä Checkout page, `magewirephp/magewire-hyva-checkout`:

- Rewrites `wire:model` → `wire:model.live`, `wire:model.defer` → `wire:model`, `wire:model.lazy` → `wire:model.blur`, `wire:model.delay.Xms` → `wire:model.live.debounce.Xms` for BC-enabled components.
- Maps V1's `$wire.sync(name, value)` onto `$wire.$set(name, value)`.
- Re-triggers deprecated JS hook names (`component.initialized`, `element.updating`, `message.sent`, …) alongside their V3 replacements.
- Proxies `component.data` → `component.$wire` and `component.deferredActions` → `component.queuedUpdates`.

Outside the Hyvä Checkout page, V1 directives are not rewritten, so migrate those templates as described under
[Breaking changes](#breaking-changes). No part of the BC layer changes `$wire.entangle('…')`; see
[Entangle is deferred by default](#entangle-is-deferred-by-default).

### What the BC layer does **not** do

You still have to manually handle:

- Custom lifecycle signatures that are not covered by the registered BC argument resolvers.
- Public property type mismatches.
- Validation rule format changes.
- Behavioural changes in Magento or Hyvä that Magewire wraps.
- Any custom JS that listens directly on internal APIs that moved.

BC buys time; it does not eliminate migration work.

### The `memo.bc.enabled` flag

BC pivots on a single flag in the snapshot memo: `memo.bc.enabled`. When present and truthy, a companion package's
directive shim activates for that component. The support Feature and deprecated PHP helpers remain registered on the
base component, so the flag should be understood as a behavior switch rather than complete removal of all BC code.

Resolution priority for the flag:

1. `#[HandleBackwardsCompatibility]` attribute (either `enabled: true` or `enabled: false`): wins in all cases.
2. Opt-in before render: `store($component)->set('magewire:bc', true)` from a Component Hook, Feature, or component resolver.
3. Companion default. Since `magewirephp/magewire-hyva-checkout` 3.1.0, a newly mounted component without an attribute is enabled when it renders inside `hyva-checkout-main`; see [Theming → Hyvä Checkout BC](../theming/hyva-checkout-bc.md).
4. Otherwise disabled.

## Breaking changes

The sections below cover the key source-verified changes. Custom integrations may depend on additional internal behavior,
so test the complete interaction rather than treating this as an exhaustive compatibility contract.

### `wire:model` is deferred by default

| V1 | V3 | Rewritten by BC? |
|---|---|---|
| `wire:model` | `wire:model.live` | On the Hyvä Checkout page |
| `wire:model.defer` | `wire:model` | On the Hyvä Checkout page |
| `wire:model.lazy` | `wire:model.blur` | On the Hyvä Checkout page |
| `wire:model.delay.500ms` | `wire:model.live.debounce.500ms` | On the Hyvä Checkout page |

V1's default was "sync on every keystroke", V3's default is "sync on form submit / next request". If you want instant sync in a V3 component, you must opt in with `.live`. The `.defer` / `.lazy` / `.delay` modifiers no longer exist in V3.

### Entangle is deferred by default

```html
<!-- V1: live by default -->
<div x-data="{ open: $wire.entangle('open') }">…</div>

<!-- V3: deferred by default. Add .live for instant sync. -->
<div x-data="{ open: $wire.entangle('open').live }">…</div>
```

BC does not change `entangle`: a bare call is deferred even in a BC-enabled component. Decide per `entangle` call whether you want live or deferred, and add `.live` where the component relied on V1's live default. Each call site may want a different answer.

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

Dispatch from PHP with `$this->dispatch('event-name', foo: 'bar')`. This replaces V1's `$this->emit('event-name', ['foo' => 'bar'])`. The BC trait keeps `emit`, `emitUp`, `emitSelf`, and `emitTo` available, but they are thin wrappers around `dispatch()` now.

### Only your own public methods are browser actions

In V3, the browser can call public methods defined on your component, but not public methods inherited from
Magewire's `Component` or `Component\Form`. A V1 template or listener that calls an inherited helper directly, such as
`wire:click="reset"`, fails with `MethodNotFoundException`. Wrap the helper in an action of your own:

```php
public function clearEmail(): void
{
    $this->reset('email');
}
```

Lifecycle hooks such as `mount`, `boot`, and `placeholder` cannot be called from the browser or used as listener
targets. Magewire 3.0.0 through 3.7.1 did not enforce all of this
([GHSA-64j9-rg74-hqc7](https://github.com/magewirephp/magewire/security/advisories/GHSA-64j9-rg74-hqc7)), so require
3.7.2 or later. See [Upgrade notes](releases/upgrade-notes.md#371-to-372).

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

The V3 `commit` hook is callback-based: the before half runs synchronously; the returned closure receives `succeed` / `fail` / `respond` continuations you can hook into. See [Component Hooks](../advanced/architecture/component-hooks.md) for the full signature.

### Component property aliases (JS)

| V1 | V3 | BC auto-handled? |
|---|---|---|
| `component.data` | `component.$wire` | Yes |
| `component.deferredActions` | `component.queuedUpdates` | Yes |

### PHP component API

| V1 | V3 | Status |
|---|---|---|
| `$this->emit('e', [...])` | `$this->dispatch('e', ...)` | V1 call kept under the BC trait; prefer `dispatch()`. |
| `$this->emitUp('e', ...)` | `$this->dispatch('e', ...)` | V3 events bubble by default; there is no `up()` modifier. |
| `$this->emitSelf('e', ...)` | `$this->dispatch('e', ...)->self()` | V1 kept; prefer `->self()` chain. |
| `$this->emitTo('other', 'e', …)` | `$this->dispatch('e', ...)->to('other')` | V1 kept; prefer `->to()` chain. |
| `$this->dispatchBrowserEvent('e', …)` | `$this->dispatch('e', ...)` and a browser event listener | V1 helper remains deprecated on the base component. `Component::js()` is not active. |
| `$this->getPublicProperties()` | `$this->all()` | V1 kept under BC trait. |
| `public $this->id` | `$this->id()` / `$this->getId()` | The deprecated public property currently remains on every base component through the BC trait. |

### Lifecycle hooks

V3 adds more lifecycle hooks than V1 exposed. All are optional:

| Hook | When it fires |
|---|---|
| `boot()` | Every request. On updates, public properties have already been restored, but `hydrate()` has not run yet. |
| `booted()` | Every request, after the mount or hydrate hook sequence. |
| `mount(...$namedArguments)` | Initial render only; receives named values from `magewire:mount:*`. |
| `hydrate()` | Every subsequent request, after public properties are restored. |
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

V1's `hydrate()` / `dehydrate()` signatures survive, while V3 adds per-property variants and `booted()`.
The framework calls trait `initialize*` hooks internally, but a plain `initialize()` method on the component is not a
public lifecycle hook in Magewire 3.7.

### `updating` / `updated` argument order

Generic V3 hooks receive the full property path followed by the new value:
`updating($fullPath, $newValue)` and `updated($fullPath, $newValue)`. Property-specific hooks receive the new value
and, for nested data, an optional key. The BC plugin can transform arguments for a BC-enabled component. Check the
`UpdatingUpdatedArgumentSwapResolver` rule if a V1 hook receives unexpected values.

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

<a id="area-scoped-di-is-required"></a>

### Register service collections in the active area

Magewire's Feature, Mechanism, Synthesizer, and Resolver arrays are configured at Magento's area-specific DI stage.
An item added to the same array in global `etc/di.xml` can be replaced when Magento loads the later frontend or
adminhtml array. Register collection items in the area where Magewire uses them.

Do not move every Magewire-related `<type>` block indiscriminately. Normal global preferences, plugins, and constructor
arguments remain valid in `etc/di.xml`; move the collection additions shown below to `etc/frontend/di.xml` and/or
`etc/adminhtml/di.xml`.

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

If you registered a V1 "feature" as a plugin or observer, consider whether it should become a real Component Hook because the middleware semantics are usually cleaner.

### Synthesizers replace V1's hydrators

V1 had a `HydratorInterface`. V3 uses **Synthesizers**: classes that explain how to serialise and deserialise a given type across the snapshot boundary.

Magewire ships synthesizers for scalars, arrays, `\stdClass`, and backed enums. A
`\Magento\Framework\DataObject` synthesizer is registered too, but its Magewire 3.7 array-cast implementation does
not guarantee a correct round trip for normal DataObject state. Keep that state in a public array until the
implementation is corrected. For custom value objects, write a `Synth` and register it:

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

Old `HydratorInterface` implementations survive under `lib/MagewireBc/Model/HydratorInterface.php` but are wrapped; convert to Synthesizers when you can.

### Alpine.js is bundled and CSP

V3 ships the CSP build of Alpine inside its JavaScript bundle. Two consequences:

- Do not start a second Alpine instance on a Magewire page. Use the maintained theme compatibility package to
  coordinate loaders instead of removing a theme's Alpine script globally.
- CSP-mode Alpine does not evaluate JavaScript expressions with `eval` / `new Function`. Arrow functions, template literals, destructuring, spread, and nested assignments inside Alpine *directive expressions* (`x-on:click="…"`, `x-init="…"`, etc.) are unavailable. Move complex logic into `Alpine.data()` registrations or a utility on `window.MagewireUtilities`.

Plain `<script>` tags in your PHTML still use normal JS; only the expressions that Alpine itself evaluates are affected.

### CSP fragments replace hand-rolled nonces

V1 templates sometimes carried hand-rolled CSP nonces or hashes on inline `<script>` tags. V3 offers **Fragments**: wrap any inline `<script>` in a fragment and Magewire injects the right nonce or hash automatically:

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

The sequence below is recommended for a module with more than a handful of V1 components. Treat each numbered step as a separate PR or commit. They are cleanest in isolation.

### 1. Install V3 with BC on everything

Add `#[HandleBackwardsCompatibility]` to every V1 component in the module. Run the test suite; visit the site. The goal here is not to change behaviour; it is to find what BC already covers. On the Hyvä Checkout page it also rewrites V1 directives. On other pages, V1 `wire:model` modifiers need step 2 before they behave as in V1.

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

If your theme or custom JS listens on `message.sent`, `element.updating`, `component.initialized`, or friends, move those listeners to the V3 names (see the rename table above). On the Hyvä Checkout page the BC layer re-triggers the old names, but removing your dependency on the old names is the cleaner end state.

### 6. Migrate PHP component calls

- `$this->emit(…)` → `$this->dispatch(…)`.
- `$this->emitUp(…)` → `$this->dispatch(…)` because V3 events bubble by default.
- `$this->emitTo('other', …)` → `$this->dispatch(…)->to('other')`.
- `$this->getPublicProperties()` → `$this->all()`.
- `$this->id` → `$this->id()` or `$this->getId()`.

### 7. Move DI registrations

Move registrations that extend the `Magewirephp\Magewire\Features` or
`Magewirephp\Magewire\Mechanisms` item collections into `etc/frontend/di.xml` and, when needed,
`etc/adminhtml/di.xml`. Normal preferences, plugins, and constructor configuration may still belong in global
`etc/di.xml`; only move configuration that is explicitly area-scoped.

### 8. Drop the BC attribute per component

As each component becomes fully V3-native, switch its attribute to
`#[HandleBackwardsCompatibility(enabled: false)]` to disable the browser transformations. When every component in
the module is V3-native, remove the attribute entirely. Keep the opt-out on components inside `hyva-checkout-main`
while `magewirephp/magewire-hyva-checkout` is installed, because its container default applies again without it.

<a id="9-remove-the-bc-feature-registration-whole-module"></a>

### 9. Remove obsolete BC integration

When every component on the site is migrated, remove the BC attributes. Do not edit Feature registration inside vendor
packages. If a companion package was installed solely to support legacy components and is no longer required, remove
that package through Composer and verify the merged layout before deployment.

## Hyvä Checkout

Hyvä Checkout V1 is wired for Livewire V2 semantics. Install `magewirephp/magewire-hyva-checkout`. Since package
3.1.0, which requires Magewire 3.7, newly mounted components without an attribute receive BC when they render inside
`hyva-checkout-main`. Add `#[HandleBackwardsCompatibility(enabled: false)]` to V3-native checkout components, add
`#[HandleBackwardsCompatibility]` to legacy components rendered outside that container, and verify the checkout end
to end.

Hyvä Checkout 1.4.0 betas can pin an affected Magewire release. Upgrade to 1.4.0-beta6 when it is available and
confirm that Magewire 3.7.2 or later is installed.

See [Theming → Hyvä Checkout BC](../theming/hyva-checkout-bc.md) for the full detail.

## Admin (new in V3)

Magewire V1 was storefront-only. V3 supports admin components through the companion package `magewirephp/magewire-admin`. If the site has admin Magewire use cases such as reactive grids, inline editors, or wizards, install it alongside core. See [Admin → Installation](../admin/installation.md) and [Admin → How it works](../admin/how-it-works.md).

Admin components use the exact same layout-XML / PHTML / `$wire` conventions as storefront. The argument name in layout XML stays `magewire` (same as storefront). The `LayoutAdminResolver` picks up admin-area blocks automatically; you never reference `layout_admin` in your own XML.

## Common upgrade gotchas

The following issues have appeared during real upgrades. Check this list before opening an issue.

- **"`wire:click` stopped working after upgrade"**: you probably still have a second Alpine loaded. Check the theme bundle and any layout XML that adds Alpine's script.
- **"Half my snapshots fail checksum validation"**: the Magento crypt key changed between the snapshot being issued and the request arriving. Flush FPC; force one page reload.
- **"CSP violations on every inline script"**: wrap inline scripts in a Script fragment. See the [CSP fragments](#csp-fragments-replace-hand-rolled-nonces) section.
- **"A V1 component I added `#[HandleBackwardsCompatibility]` to still behaves V3"**: the attribute import is most likely wrong. The correct namespace is `Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility`.
- **"`$this->emit` is used by migrated code"**: the current base component still carries the deprecated helper, but
  new code should use `$this->dispatch()` so it does not depend on a compatibility trait that may be removed later.
- **"My observer listening on `message.sent` stopped firing"**: the JS-side hook is now `commit`. For server-side observer events see the table in [Features](../advanced/architecture/features.md#faq).
- **"My Feature's `provide()` is never called"**: confirm it is an item on `Magewirephp\Magewire\Features` in the
  active area's `etc/frontend/di.xml` or `etc/adminhtml/di.xml`. A global array addition can be replaced by the later
  area-specific DI configuration.
- **"An `entangle` value no longer reaches the server immediately"**: a bare `$wire.entangle('…')` is deferred in V3, and BC does not change it. Add `.live` where each change must be sent immediately.
- **"A migrated checkout component behaves like V1 again"**: since `magewirephp/magewire-hyva-checkout` 3.1.0, components inside `hyva-checkout-main` without an attribute receive BC. Add `#[HandleBackwardsCompatibility(enabled: false)]`.
- **"`$wire.sync()` fails with a public method `sync` not found error"**: V1's `$wire.sync()` is mapped onto `$wire.$set()` only on the Hyvä Checkout page with `magewirephp/magewire-hyva-checkout` 3.1.0 or later. Use `$wire.$set(name, value)`.

## Verifying the upgrade

After migrating, confirm the end state:

1. **No V1 directive lingers.**
   ```bash
   grep -rEn "wire:model(\.defer|\.lazy|\.delay)" app/code your-theme/
   ```
2. **No V1 hook name lingers.** Search JS for `message.sent`, `component.initialized`, `element.updating`, `element.removed`.
3. **No V1 PHP helper lingers.** Search for `->emit(`, `->emitUp(`, `->emitSelf(`, `->emitTo(`, `->dispatchBrowserEvent(`, `->getPublicProperties(`, `$this->id` accesses.
4. **No area-scoped service collection is registered globally.**
   ```bash
   grep -lrn "Magewirephp\\\\Magewire" app/code/**/etc/di.xml
   ```
   Inspect each match. Move only Features, Mechanisms, Hooks, Synthesizers, and Resolvers that extend area-scoped
   collections. Keep valid global preferences, plugins, and constructor configuration where they belong.
5. **No component still carries `#[HandleBackwardsCompatibility]`** after migration. A repo-wide grep proves the migration is complete.
6. **Site health.** Click through the top ten most-trafficked Magewire components, watching the browser devtools Network tab for 4xx/5xx on `/magewire/update` and the console for CSP violations or Alpine warnings.

## Rolling back

If the upgrade surfaces a showstopper bug, you can roll back to V1 by restoring the previous `composer.lock`, running `composer install`, and flushing caches. Any V3-specific code (the `#[HandleBackwardsCompatibility]` attribute, `->dispatch()->to()` chains, `#[On]` attributes) will need to be reverted first; V1 will not understand them. Keep the migration PR small enough that the revert is reasonable.

## Migration checklist

Copy this into a PR description.

- [ ] PHP is on 8.2+ and the Magento or Mage-OS release is supported by the selected Magewire tag.
- [ ] Composer updated to `magewirephp/magewire:^3.7.2`.
- [ ] `magewirephp/magewire-admin` installed if the site uses Magewire in admin.
- [ ] The theme compatibility package ensures only one Alpine runtime starts on pages with and without Magewire components.
- [ ] Every existing component carries `#[HandleBackwardsCompatibility]` (imported from `Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\`).
- [ ] `wire:model.defer` → `wire:model`.
- [ ] `wire:model.lazy` → `wire:model.blur`.
- [ ] Bare `wire:model` → `wire:model.live` where instant sync is required.
- [ ] `wire:model.delay.Xms` → `wire:model.live.debounce.Xms`.
- [ ] Every `$wire.entangle('…')` audited: `.live` added where needed.
- [ ] Every `protected $listeners = […]` replaced with `#[On('event-name')]` attributes.
- [ ] Every `$this->emit*()` migrated to `$this->dispatch()` (with `->self()` or `->to()` where appropriate; events bubble without `->up()`).
- [ ] Every `$this->getPublicProperties()` migrated to `$this->all()`.
- [ ] Every `$this->id` access migrated to `$this->id()` / `$this->getId()`.
- [ ] Every deprecated JS hook name (`message.sent`, `component.initialized`, `element.updating`, `element.removed`) migrated to the V3 name.
- [ ] Every `component.data` / `component.deferredActions` JS access migrated to `component.$wire` / `component.queuedUpdates`.
- [ ] Every area-scoped Feature / Mechanism / Hook / Synthesizer / Resolver collection registration moved from global `etc/di.xml` to `etc/frontend/di.xml` (and `etc/adminhtml/di.xml` as needed).
- [ ] Inline `<script>` tags wrapped in Script fragments where CSP compliance matters.
- [ ] Custom `HydratorInterface` implementations rewritten as Synthesizers.
- [ ] `render(): string` methods replaced by `rendering()` hooks that call `magewireBlock()->setTemplate(...)`.
- [ ] BC attribute set to `enabled: false` (or removed) on fully migrated components. Keep `enabled: false` on components inside `hyva-checkout-main` while `magewirephp/magewire-hyva-checkout` is installed.
- [ ] Smoke-tested against the top-trafficked components (devtools Network + console).

Migration done. Remove obsolete BC attributes and any package used only for the legacy integration when every module on
the site has reached this state.

## Related

- [Backwards compatibility](../essentials/backwards-compatibility.md): the BC system in depth.
- [Hyvä Checkout BC](../theming/hyva-checkout-bc.md): the container default, opt-outs, and the checkout shims.
- [Admin → Installation](../admin/installation.md): install the admin companion package.
- [Features](../advanced/architecture/features.md): how to rewrite V1 Features as V3 Component Hooks.
- [Synthesizers](../advanced/synthesizers.md): replacement for V1 hydrators.
