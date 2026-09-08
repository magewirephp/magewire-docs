# Backwards Compatibility

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Magewire V3 is a full rewrite on top of Livewire V3, which changed a number of conventions from the
V1 (Livewire V2) era. To keep existing V1 components running while you migrate, Magewire ships a
**backwards-compatibility (BC) layer**.

The browser transformations are **opt-in and per-component**. The current base component still includes deprecated PHP
helpers, and the registered BC Feature itself has no per-component `skip()` guard. This page separates those
always-present pieces from behavior controlled by the component flag. For the current Hyvä Checkout limitation, see
[Hyvä Checkout BC](../theming/hyva-checkout-bc.md).

## Two scopes of enable / disable

There are two independent switches. Most of the time you only touch the first.

| Scope | What it controls | Default |
|---|---|---|
| **Per component** | Whether an individual component receives BC behaviour. | Off (no BC) |
| **The whole feature** | Whether the BC subsystem is registered at all, site-wide. | On (registered) |

## Per-component: the `#[HandleBackwardsCompatibility]` attribute

The supported, explicit way to opt a component in is the attribute on the component class:

```php
use Magewirephp\Magewire\Component;
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class LegacyCart extends Component
{
    // Runs with V1 backwards compatibility enabled.
}
```

Pass `enabled: false` to opt **out** explicitly, which is handy when a theme rule would otherwise enable BC
for this component (see resolution order below):

```php
#[HandleBackwardsCompatibility(enabled: false)]
class ModernCart extends Component
{
    // Forced off, even when a theme integration supplies a BC default.
}
```

The `LayoutResolver` reads this attribute when it constructs the component and writes the result to
an internal per-component flag (`magewire:bc` in the component's data store). The browser shims and lifecycle
argument adapter key off that flag. Deprecated PHP helpers and the registered server-side BC Feature remain present.

### Programmatic toggle

From a [Component Hook](../advanced/architecture/component-hooks.md) or a Feature that needs to
decide per request, set the flag directly:

```php
use function Magewirephp\Magewire\store;

store($component)->set('magewire:bc', true);
```

### Resolution order

When more than one source has an opinion, the flag resolves in this order:

1. **Explicit attribute**: `#[HandleBackwardsCompatibility]` (either value) wins.
2. **Data-store value**: a programmatically set `magewire:bc` flag.
3. **Default**: the layout resolver writes `false` when neither of the earlier sources provided a value.

A companion package may attempt to supply a theme or container default later, but that is not dependable when it checks
for an unset value after the core resolver has already written `false`. Use explicit attributes.

## What the BC layer does

BC enabling activates several adaptations, on both the PHP and JavaScript sides.

<a id="php-side-framework-theme-agnostic"></a>

### PHP side (core framework)

- **Deprecated V1 component APIs.** The base `Component` mixes in the
  `HandlesComponentBackwardsCompatibility` trait, which keeps V1-era methods and properties working:
  `getPublicProperties()` (the V2 equivalent of `all()`), the public `$id` property, and the Emit,
  Error, BrowserEvent, Request and View concerns. These exist on every component, but are only
  meaningful to code written against the old API.
- **Snapshot effects.** The `SupportMagewireBackwardsCompatibility` Feature is registered at sort order `99100`.
  In Magewire 3.6 it has no `skip()` guard, so it initializes for every component. It rebuilds V1-style request data
  on `hydrate()` and pushes a `bc` effect containing the property-path map on `dehydrate()`. The component flag
  controls whether the browser shim applies V1 behavior.
- **Lifecycle-hook argument adaptation.** For BC-enabled components only, a plugin on the lifecycle
  feature rewrites V1 hook call signatures to their V3 form before dispatch: for example the
  argument order of `updatingFoo()` / `updatedFoo()`. V1 hook methods keep being called correctly
  without you rewriting their signatures.

### JavaScript side (theme shim)

The per-component flag reaches the browser as `memo.bc.enabled`. When present and truthy, a theme's
BC shim activates for that component's DOM subtree and applies the V2→V3 transforms automatically;
when absent or false, the shim sleeps, so non-BC components avoid the browser-side transformations. With BC active it:

- rewrites `wire:model` to `wire:model.live` (V1's default was live);
- rewrites `wire:model.defer` to `wire:model`, and `wire:model.lazy` to `wire:model.blur`;
- rewrites `wire:model.delay.Xms` to `wire:model.live.debounce.Xms`;
- returns a **live-by-default** proxy from `$wire.entangle()`;
- re-fires deprecated hook names (`component.initialized`, `element.updating`, `message.sent`, …)
  alongside their V3 replacements, so V1 JavaScript listening on old names keeps working;
- aliases `component.data` and `component.deferredActions` to `component.$wire` and
  `component.queuedUpdates`.

This shim lives in the theme compatibility module (see
[Compatibility module](../theming/compatibility-module.md)). Themes may also add their own BC
behaviour on top. The Hyvä Checkout companion attempts a container-based default, but Magewire 3.6 migrations must use
explicit attributes; see [Hyvä Checkout BC](../theming/hyva-checkout-bc.md).

### V1 → V3 cheat sheet

The directive and `entangle` defaults that changed between versions:

| V1 / V2 | V3 | Behaviour |
|---|---|---|
| `wire:model` | `wire:model.live` | Sync on every change (instant) |
| `wire:model.defer` | `wire:model` | Sync on submit / next request (now the default) |
| `wire:model.lazy` | `wire:model.blur` | Sync on blur |
| `$wire.entangle('p')` (live) | `$wire.entangle('p').live` | Opt back in to live; bare `entangle` is now deferred |

For a BC-enabled component the theme shim applies these rewrites automatically. When you migrate the
component for real, update the markup to the V3 column and drop BC.

## What BC does *not* cover

BC buys time; it does not eliminate migration work. It will **not** fix:

- Changed component **method signatures** between V1 and V3.
- Public property **type** mismatches.
- **Validation-rule** format changes.
- Behavioural changes in the underlying Magento or theme code that Magewire wraps.

These still require manual changes. See the [Upgrade](../getting-started/upgrade.md) checklist.

<a id="disabling-the-whole-feature"></a>

## Disabling the server Feature

BC is registered as a [Feature](../advanced/architecture/features.md) named
`magewire_backwards_compatibility`. Once every component is V3-native, disable its server hook by overriding the
feature item to `false` in your module's **area-scoped** DI
(`etc/frontend/di.xml`, and `etc/adminhtml/di.xml` if relevant):

```xml title="etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Features">
    <arguments>
        <argument name="items" xsi:type="array">
            <!-- Disable the framework BC feature entirely. -->
            <item name="magewire_backwards_compatibility" xsi:type="boolean">false</item>
        </argument>
    </arguments>
</type>
```

A Feature item set to `false` is filtered out before booting, so this Component Hook does not register. The deprecated
methods on the base `Component` and browser scripts supplied by a companion package are separate and remain in their
own code.

!!! warning "Only disable once you're fully migrated"
    Turning the server Feature off removes its hydration and dehydration behavior for **every** component at once,
    regardless of any `#[HandleBackwardsCompatibility]` attributes. Do this only when no component, in any module,
    still depends on V1 behaviour. To drop BC for a single component, prefer
    `#[HandleBackwardsCompatibility(enabled: false)]`.

## Recommended migration flow

1. Install V3 alongside your V1 module and add `#[HandleBackwardsCompatibility]` to every legacy
   component. Test every interaction; the attribute is not a guarantee that unchanged V1 code will work.
2. Migrate one component at a time using the [Upgrade](../getting-started/upgrade.md) checklist.
3. When a component is fully V3-native, switch its attribute to
   `#[HandleBackwardsCompatibility(enabled: false)]` to disable the browser transformations, then remove the
   attribute once you are confident.
4. When the whole site is migrated, [disable the server Feature](#disabling-the-server-feature). Remove a companion
   package through Composer if it was installed only for legacy browser shims; do not edit vendor DI or layout files.

## Performance impact

The BC shim runs on every morph for every BC-enabled component. The cost per morph is:

- one pass over the element's `wire:*` attributes (directive rewriting);
- one `Proxy` wrapper around the component's `$wire` (entangle semantics);
- one extra event dispatch per deprecated hook name during each commit.

The exact cost depends on component size and browser workload. Treat BC as a migration aid, measure it in the target checkout, and switch it off per component as migration finishes.

## Related

- [Hyvä Checkout BC](../theming/hyva-checkout-bc.md): explicit opt-in and the current container-fallback limitation.
- [Compatibility module](../theming/compatibility-module.md): where a theme's BC shim and features live.
- [Upgrade](../getting-started/upgrade.md): the V1 → V3 migration checklist.
- [Features](../advanced/architecture/features.md): how the BC feature is registered and booted.
