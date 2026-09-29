# Hyvä Checkout Backwards Compatibility

Hyvä Checkout V1 was built on Magewire V1, which tracked Livewire V2. The
`magewirephp/magewire-hyva-checkout` package contains browser shims for running those components on Magewire 3.

The package requires `magewirephp/magewire-hyva-theme` and Hyvä Checkout. Its scripts load only on the
`hyva_checkout_index_index` layout handle, so they do not affect other storefront pages.

| Package release | Requires `magewirephp/magewire` |
|---|---|
| 3.0.0 | `>=3.2` |
| 3.1.0 | `>=3.7` |
| 3.1.1 | `~3.7.1` |

!!! warning "Behavior change in 3.1.0"
    In 3.0.0, the core layout resolver wrote an explicit `false` value before the package checked for an unset
    one, so the container fallback never enabled BC. From 3.1.0, a newly mounted component without an attribute
    receives BC when it renders inside `hyva-checkout-main`. A V3-native checkout component that has no attribute
    starts receiving the V1 browser transformations, for example `wire:model` becomes `wire:model.live`. Add
    `#[HandleBackwardsCompatibility(enabled: false)]` to those components before upgrading.

<a id="the-automatic-rule"></a>

## How a checkout component's BC state is decided

When a component is first rendered (mounted), the package resolves its BC flag in this order:

1. **Class attribute.** `#[HandleBackwardsCompatibility]` enables BC and
   `#[HandleBackwardsCompatibility(enabled: false)]` disables it. The attribute always wins.
2. **Resolver opt-in.** A component resolver may set the `magewire:bc` flag to `true` before the component renders.
   Hyvä Checkout's component resolver (`hyva_checkout_component`) does this for the components it resolves. Kept since
   3.1.1.
3. **Container fallback.** The component renders inside the `hyva-checkout-main` block.
4. **Default.** Otherwise BC is disabled.

The result is sent to the browser as `memo.bc.enabled`. On later update requests the package reuses the value from
the snapshot instead of resolving it again, although a class attribute still takes precedence.

Setting `store($component)->set('magewire:bc', false)` before the first render does not disable BC for a component
inside `hyva-checkout-main`, because the container fallback is applied on top of it. Use the attribute to opt out.

<a id="opting-out-per-component"></a>

## Opting out V3-native components

Mark every checkout component that already uses V3 directives, events, and hooks:

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility(enabled: false)]
class DeliveryNote extends \Magewirephp\Magewire\Component { /* ... */ }
```

Keep the opt-out while this package is installed. Removing the attribute puts the component back under the container
fallback.

## Opting in outside the container

A legacy component rendered outside `hyva-checkout-main`, and not resolved by Hyvä Checkout's component resolver,
starts with BC disabled. Add the attribute to enable it:

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class CheckoutShipping extends \Magewirephp\Magewire\Component { /* ... */ }
```

An explicit attribute is also the most predictable choice for legacy components inside the container, because it does
not depend on where or when the component is rendered.

<a id="dynamic-components"></a>

## Components mounted during an update request

A component can be mounted for the first time during a later Magewire update request, for example a payment method
renderer that appears after the customer selects that method. That render starts from the updated component rather
than from `hyva-checkout-main`, so the container fallback does not apply.

Such a component keeps BC when Hyvä Checkout's component resolver opted it in (package 3.1.1 and later) or when its
class carries `#[HandleBackwardsCompatibility]`. In package 3.1.0 the fallback replaced the resolver's opt-in, which
disabled BC for these components. Legacy `wire:model.delay` fields in such a renderer then stopped syncing.

## What the Hyvä BC layer does (under the hood)

The package registers four scripts in the `magewire.features.support-hyva-checkout-backwards-compatibility`
container, inside `magewire.features`, on the `hyva_checkout_index_index` handle:

| File | Role | Applies to |
|---|---|---|
| `magewire-attributes.phtml` | Rewrites `wire:model` / `.defer` / `.lazy` / `.delay.Xms` on `element.init` and `morph.updating`. | Components with `memo.bc.enabled` |
| `magewire-components.phtml` | Wraps each component's `$wire` once on `component.init`. `$wire.sync()` is mapped onto `$wire.$set()`, and `$wire.__instance` (also reached through `Magewire.find(id).__instance`) returns a component proxy that resolves V1 aliases and a V1-style `call()`. | Every component on the checkout page |
| `magewire-events.phtml` | Re-triggers deprecated hooks (`component.initialized` etc.) from their V3 replacements. Aliases `component.data` and `component.deferredActions`. | Every component on the checkout page |
| `magewire-hooks.phtml` | Promise-based runner for the deprecated hook names. Warns once per hook name in the browser console when Magewire runs in developer mode. | Every component on the checkout page |

Only the directive rewrite reads `memo.bc.enabled`. The other shims keep deprecated JavaScript APIs available to any
checkout script that still calls them.

### `$wire.sync()`

Magewire V1's `$wire.sync(name, value)` has no V3 equivalent. Without the proxy it is sent as a call to a component
method named `sync`, and the request fails because the component has no public `sync` method. Since package 3.1.0 the proxy maps it onto
`$wire.$set(name, value, live)` with `live` defaulting to `true`, so the value is sent immediately. Use `$wire.$set()`
in V3-native code.

### `$wire.entangle()` is not converted

None of the shims change `$wire.entangle()`. A bare `entangle` call is deferred in V3, including in BC-enabled
components. Add `.live` where legacy code relied on V1's live-by-default behavior.

## Release notes

| Package release | BC changes |
|---|---|
| 3.0.0 | Container fallback never fired, because the core resolver wrote `false` first. Legacy components needed an explicit attribute unless a resolver opted them in. |
| 3.1.0 | Container fallback restored. `$wire.sync()` mapped onto `$set()`. The `$wire` proxy is applied to every checkout component instead of only BC-enabled ones. |
| 3.1.1 | A resolver opt-in is kept for newly mounted components, including components mounted during an update request. |

## Removing the BC layer

When every Hyvä Checkout component on your installation is V3-native:

1. While this package is installed, keep `#[HandleBackwardsCompatibility(enabled: false)]` on V3-native components
   inside `hyva-checkout-main`, and remove `#[HandleBackwardsCompatibility]` opt-ins elsewhere.
2. Do not edit DI configuration inside a vendor package.
3. If `magewirephp/magewire-hyva-checkout` was installed only for legacy BC and is no longer needed, remove it through
   Composer. The package also groups repeated checkout flash messages; that behavior is removed with it.
4. Flush cache and run the checkout end to end.

## Related

- [Backwards compatibility](../essentials/backwards-compatibility.md): the underlying system.
- [Upgrade](../getting-started/upgrade.md): V1 → V3 migration checklist.
- [Compatibility module](compatibility-module.md): how Hyvä's compat module is organised.
