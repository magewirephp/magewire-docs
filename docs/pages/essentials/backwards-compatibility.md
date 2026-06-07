# Backwards Compatibility

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Magewire V3 is a full rewrite on top of Livewire V3, which changed a number of conventions from the
V1 (Livewire V2) era. To keep existing V1 components running while you migrate, Magewire ships a
**backwards-compatibility (BC) layer**.

BC is **opt-in and per-component**: a component only gets BC treatment when you ask for it, so
modern components pay no cost. This page covers the framework side — how to switch BC on and off,
and what it actually does. For the theme-side JavaScript shim (directive rewriting, `entangle`
semantics, deprecated hook names) and Hyvä's auto-enable rule, see
[Theming → Backwards Compatibility](../theming/backwards-compatibility.md).

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

Pass `enabled: false` to opt **out** explicitly — handy when a theme rule would otherwise enable BC
for this component (see resolution order below):

```php
#[HandleBackwardsCompatibility(enabled: false)]
class ModernCart extends Component
{
    // Forced off, even under a theme that auto-enables BC.
}
```

The `LayoutResolver` reads this attribute when it constructs the component and writes the result to
an internal per-component flag (`magewire:bc` in the component's data store). Everything else in the
BC layer keys off that flag.

### Programmatic toggle

From a [Component Hook](../advanced/architecture/component-hooks.md) or a Feature that needs to
decide per request, set the flag directly:

```php
use function Magewirephp\Magewire\store;

store($component)->set('magewire:bc', true);
```

### Resolution order

When more than one source has an opinion, the flag resolves in this order:

1. **Explicit attribute** — `#[HandleBackwardsCompatibility]` (either value) wins.
2. **Data-store value** — a programmatically set `magewire:bc` flag.
3. **Theme default** — a theme compatibility module may enable BC for whole groups of components
   (e.g. everything inside a checkout container). See the theme's BC documentation.

If none apply, the flag defaults to `false` and the component runs as pure V3.

## What the BC layer does

BC enabling activates several adaptations, on both the PHP and JavaScript sides.

### PHP side (framework, theme-agnostic)

- **Deprecated V1 component APIs.** The base `Component` mixes in the
  `HandlesComponentBackwardsCompatibility` trait, which keeps V1-era methods and properties working —
  `getPublicProperties()` (the V2 equivalent of `all()`), the public `$id` property, and the Emit,
  Error, BrowserEvent, Request and View concerns. These exist on every component, but are only
  meaningful to code written against the old API.
- **Snapshot effects for legacy clients.** The `SupportMagewireBackwardsCompatibility` feature
  (registered at sort order `99100`) rebuilds the V1-style server memo on `hydrate()`, and on
  `dehydrate()` pushes a `bc` effect into the snapshot containing a property-path map
  (`data` → `$wire`, `__livewire` → `queuedUpdates`). V1-era JavaScript uses this map to find
  properties that moved in V3.
- **Lifecycle-hook argument adaptation.** For BC-enabled components only, a plugin on the lifecycle
  feature rewrites V1 hook call signatures to their V3 form before dispatch — for example the
  argument order of `updatingFoo()` / `updatedFoo()`. V1 hook methods keep being called correctly
  without you rewriting their signatures.

### JavaScript side (theme shim)

When the per-component flag reaches the browser as `memo.bc.enabled`, a theme's BC shim rewrites
`wire:*` directives, restores `entangle`'s live-by-default behaviour, and re-fires deprecated hook
names alongside their V3 replacements. That layer lives in the theme compatibility module and is
documented in [Theming → Backwards Compatibility](../theming/backwards-compatibility.md).

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

These still require manual changes — see the [Upgrade](../getting-started/upgrade.md) checklist.

## Disabling the whole feature

BC is registered as a [Feature](../advanced/architecture/features.md) named
`magewire_backwards_compatibility`. To remove the entire subsystem site-wide — once every component
is V3-native — override the feature item to `false` in your module's **area-scoped** DI
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

A feature item set to `false` is filtered out before booting, so the BC feature never registers.

!!! warning "Only disable once you're fully migrated"
    Turning the feature off removes BC for **every** component at once, regardless of any
    `#[HandleBackwardsCompatibility]` attributes. Do this only when no component — in any module —
    still depends on V1 behaviour. To drop BC for a single component, prefer
    `#[HandleBackwardsCompatibility(enabled: false)]`.

## Recommended migration flow

1. Install V3 alongside your V1 module and add `#[HandleBackwardsCompatibility]` to every legacy
   component. The site runs with no V1 code changes.
2. Migrate one component at a time using the [Upgrade](../getting-started/upgrade.md) checklist.
3. When a component is fully V3-native, switch its attribute to
   `#[HandleBackwardsCompatibility(enabled: false)]` so it stops paying the BC cost — then remove the
   attribute once you're confident.
4. When the whole site is migrated, [disable the feature](#disabling-the-whole-feature) to drop the
   BC code (and the theme's JS shim) entirely.

## Related

- [Theming → Backwards Compatibility](../theming/backwards-compatibility.md) — the JavaScript shim and the `memo.bc.enabled` flag.
- [Theming → Hyvä Checkout BC](../theming/hyva-checkout-bc.md) — the canonical theme auto-enable rule.
- [Upgrade](../getting-started/upgrade.md) — the V1 → V3 migration checklist.
- [Features](../advanced/architecture/features.md) — how the BC feature is registered and booted.
