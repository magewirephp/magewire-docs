# Backwards Compatibility

Magewire V3 ships a backwards-compatibility (BC) layer that lets V1 components run on V3 without code changes. The layer has two halves: a PHP flag in the snapshot memo and a JavaScript shim that reads the flag and applies V2→V3 transforms on the fly.

The BC layer is **opt-in** per component. This page covers the core system; theme-specific rules (for example, Hyvä Checkout's auto-enable rule) are documented on their own pages.

## What it handles automatically

When BC is enabled for a component:

- `wire:model` rewrites to `wire:model.live` (V1's default was live).
- `wire:model.defer` rewrites to `wire:model`.
- `wire:model.lazy` rewrites to `wire:model.blur`.
- `wire:model.delay.Xms` rewrites to `wire:model.live.debounce.Xms`.
- `$wire.entangle()` returns a live-by-default proxy.
- Deprecated hook names (`component.initialized`, `element.updating`, `message.sent`, etc.) are re-triggered alongside their V3 replacements, so V1 JS listening on old names keeps working.
- `component.data` and `component.deferredActions` proxy to `component.$wire` and `component.queuedUpdates`.

## What it does NOT handle

- Component method signature changes between V1 and V3.
- Public property type mismatches.
- Removed APIs (`$this->id`, `$this->getPublicProperties()` — though a trait exists).
- Validation-rule format changes.
- Behavioural changes in Magento or Hyvä that Magewire wraps.

You still need to manually update code for everything above. BC buys time; it does not eliminate migration work.

## The memo flag

BC pivots on a single flag in the snapshot memo: `memo.bc.enabled`. When present and truthy, the JavaScript shim activates for that component's DOM subtree. Otherwise, the shim sleeps — so unaffected components pay no runtime cost.

## Enabling BC on a component

Three mechanisms, resolved in priority order:

### 1. PHP attribute (explicit)

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class LegacyCart extends \Magewirephp\Magewire\Component { /* … */ }

// Opt out explicitly — useful to override a theme-level auto-enable rule:
#[HandleBackwardsCompatibility(enabled: false)]
class ModernCart extends \Magewirephp\Magewire\Component { /* … */ }
```

### 2. Programmatic

```php
use function Magewirephp\Magewire\store;

store($component)->set('magewire:bc', true);
```

Useful from a Component Hook or a Feature that decides per-request whether to opt the component in.

### 3. Theme default (implicit)

A theme compatibility module can ship a Feature that inspects the component and flips the flag based on heuristics. Hyvä's Checkout BC module does this for components rendered inside the `hyva-checkout-main` container — see [Hyvä Checkout BC](hyva-checkout-bc.md).

Priority order when more than one applies:

1. Explicit attribute (either `enabled: true` or `enabled: false`) wins.
2. Data-store value wins over theme defaults.
3. Theme default applies only when neither of the above is set.

## Migration workflow

Recommended flow for an existing V1 module:

1. Install Magewire V3 alongside the V1 module. Add `#[HandleBackwardsCompatibility]` to every legacy component. Site runs; no V1 code changes required.
2. Migrate one component at a time (see [Upgrade](../getting-started/upgrade.md) checklist).
3. When a component is fully V3-native, switch its attribute to `#[HandleBackwardsCompatibility(enabled: false)]` — that component no longer pays the BC-shim runtime cost.
4. When **every** component in the module is V3-native, remove the attribute entirely.
5. When every module on the site is migrated, remove the BC feature registration from your theme compat module's DI to drop the JS shim bundle.

## Performance impact

The BC shim runs on every morph for every BC-enabled component. Cost is:

- One pass over the element's `wire:*` attributes per morph (directive rewriting).
- One Proxy wrapper around the component's `$wire` (entangle semantics).
- One additional event dispatch per deprecated hook name during each commit.

In practice this is sub-millisecond per morph — negligible for individual components, not negligible if BC is globally enabled on a site with hundreds of components.

## Related

- [Upgrade](../getting-started/upgrade.md) — V1 → V3 migration checklist.
- [Hyvä Checkout BC](hyva-checkout-bc.md) — the canonical theme-specific BC rule.
- [Compatibility module](compatibility-module.md) — where theme BC features live.
