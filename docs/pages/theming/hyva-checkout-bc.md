# Hyvä Checkout Backwards Compatibility

Hyvä Checkout V1 was built on Magewire V1, which tracked Livewire V2. Most installations carry dozens of V1-era checkout components. To smooth the Magewire V3 upgrade without forcing a full rewrite, Magewire's Hyvä compatibility module auto-enables the [BC layer](backwards-compatibility.md) for every component inside the `hyva-checkout-main` layout container.

## The automatic rule

Any component rendered inside (or nested under) the `hyva-checkout-main` container has its `memo.bc.enabled` flag set to `true` unless explicitly overridden.

```
hyva-checkout-main
├── CheckoutShipping           → BC enabled
├── CheckoutPayment            → BC enabled
│   └── PaymentMethodSelector  → BC enabled (parent is BC)
└── CheckoutSummary            → BC enabled
```

This covers the V1 checkout's entire component tree without touching a single PHP class.

## Opting out per component

Once you rewrite a checkout component to be V3-native end-to-end, opt it out so it stops paying the shim cost:

```php
use Magewirephp\Magewire\Attributes\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility(enabled: false)]
class CheckoutShipping extends \Magewirephp\Magewire\Component { /* … */ }
```

The explicit attribute beats the container rule.

## Opting in outside the container

For a legacy component rendered **outside** `hyva-checkout-main` (a mini-cart, a CMS widget):

```php
#[HandleBackwardsCompatibility]
class MiniCart extends \Magewirephp\Magewire\Component { /* … */ }
```

## Dynamic components

For components injected dynamically (after initial render), the container rule checks the parent's BC status via a hydration registry. A child rendered into a BC-enabled parent inherits BC automatically. Components injected into non-BC parents without the attribute default to BC-disabled.

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

When every Hyvä Checkout component on your install is V3-native:

1. Remove `#[HandleBackwardsCompatibility]` attributes where present.
2. Remove the Hyvä Checkout BC Feature from your theme compat module's `etc/frontend/di.xml`.
3. Flush cache and run the checkout end-to-end.

If any checkout component was relying on the automatic rule without the attribute, it will now break — adding the attribute explicitly is a safe intermediate step.

## Related

- [Backwards compatibility](backwards-compatibility.md) — the underlying system.
- [Upgrade](../getting-started/upgrade.md) — V1 → V3 migration checklist.
- [Compatibility module](compatibility-module.md) — how Hyvä's compat module is organised.
