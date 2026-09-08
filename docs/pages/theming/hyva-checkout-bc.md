# Hyvä Checkout Backwards Compatibility

Hyvä Checkout V1 was built on Magewire V1, which tracked Livewire V2. The
`magewirephp/magewire-hyva-checkout` package contains browser shims for running those components on Magewire 3.

!!! warning "Use explicit attributes with Magewire 3.6"
    The core layout resolver writes an explicit false BC value before the companion package's container fallback checks
    for an unset value. The fallback therefore does not enable BC automatically in the current source. Add the
    attribute explicitly to every legacy checkout component and verify its interactions.

<a id="the-automatic-rule"></a>
<a id="opting-out-per-component"></a>
<a id="opting-in-outside-the-container"></a>

## Explicit opt-in

Add the attribute to every legacy component that needs Livewire V2-style browser behavior, regardless of where it is
rendered:

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class CheckoutShipping extends \Magewirephp\Magewire\Component { /* ... */ }
```

Once the component is V3-native, remove the attribute. An explicit
`#[HandleBackwardsCompatibility(enabled: false)]` can be used temporarily when another integration attempts to opt
the component in, but it is not required under the current false default.

<a id="dynamic-components"></a>

## Container and parent fallbacks

The companion package contains two fallback ideas:

- enable components inside `hyva-checkout-main`;
- inherit BC status from a parent through its hydration registry.

Neither is a substitute for explicit attributes in Magewire 3.6. The layout-container fallback is bypassed by the
core resolver's false default, and dynamic or nested component behavior must be verified independently.

## What the Hyvä BC layer does (under the hood)

The compat module ships four phtml scripts that together implement the shim:

| File | Role |
|---|---|
| `magewire-attributes.phtml` | Rewrites `wire:model` / `.defer` / `.lazy` / `.delay.Xms` on `element.init` and `morph.updating`. |
| `magewire-hooks.phtml` | Promise-based runner for deprecated hook names. Warns once per hook in debug mode. |
| `magewire-events.phtml` | Re-triggers deprecated events (`component.initialized` etc.) from their V3 replacements. Aliases `component.data`, `component.deferredActions`. |
| `magewire-components.phtml` | Proxies `Magewire.find(id).__instance` so `$wire.entangle()` is live-by-default inside BC components. |

All four are registered into the `magewire.internal.backwards-compatibility` container. They only run when `memo.bc.enabled` is truthy on the component.

## Removing the BC layer

When every Hyvä Checkout component on your installation is V3-native:

1. Remove `#[HandleBackwardsCompatibility]` attributes where present.
2. Do not edit DI configuration inside a vendor package.
3. If `magewirephp/magewire-hyva-checkout` was installed only for legacy BC and is no longer needed, remove it through
   Composer.
4. Flush cache and run the checkout end to end.

## Related

- [Backwards compatibility](../essentials/backwards-compatibility.md): the underlying system.
- [Upgrade](../getting-started/upgrade.md): V1 → V3 migration checklist.
- [Compatibility module](compatibility-module.md): how Hyvä's compat module is organised.
