# FAQ

## What is Magewire?

Magewire is a server-driven UI framework for Magento 2. A component keeps its state and actions in PHP, renders through
a Magento `.phtml` template, and updates the existing page through a small browser runtime.

Magewire follows Livewire 3 concepts while integrating component construction, templates, requests, and configuration
with Magento.

## When is Magewire a good fit?

Magewire is useful when an interaction is naturally owned by server-side Magento code but still needs a responsive UI:
forms, selectors, configurators, cart tools, checkout steps, and account features are common examples.

Use ordinary server-rendered blocks for static output and Alpine for state that exists only in the browser. Choose a
Magewire component when the browser and PHP need to share state or invoke server-side behavior repeatedly without a full
page reload.

## How is Magewire versioned?

Magewire follows [semantic versioning](https://semver.org/), and its major version tracks Livewire's major version. That
is why Magewire V2 was skipped. Companion packages adopt the Magewire major they support, so packages such as
`magewirephp/magewire-hyva-theme` start their current line at `3.x`.

See [Versioning](versioning.md) for the complete policy.

## What are the main differences between V1 and V3?

Magewire V3 is a substantial rewrite built much closer to Livewire 3. It has a modular Feature and Mechanism
architecture, a new component resolver and request path, signed snapshots, a newer browser runtime, and different
property-binding defaults.

It includes a backwards-compatibility layer for common V1 behavior, but it is not a drop-in replacement for every V1
extension. See [V3 vs V1](v3-vs-v1.md) and the [Upgrade Guide](upgrade.md) before migrating custom components.

## Is Magewire V1 still supported?

No. Feature development stopped earlier, and the announced security-maintenance window ended on **January 1, 2026**.
V1 is now unsupported.

Upgrade to Magewire 3. Report suspected vulnerabilities privately according to the security policy in the current
Magewire repository rather than opening a public issue with sensitive details.

## Does V3 contain every V1 feature?

There is no permanent one-to-one feature checklist: V3 replaces some V1 behavior, ports some through its compatibility
layer, and deliberately leaves other internals behind. The commonly used component lifecycle and directive workflows
are available, while custom V1 integrations may need to be redesigned.

Use [V3 vs V1](v3-vs-v1.md) for conceptual differences and the [Feature History](releases/feature-history.md) for the
released V3 surface.

## Can I upgrade an existing V1 component?

Yes. The [Upgrade Guide](upgrade.md) covers namespace changes, lifecycle semantics, property binding, JavaScript hooks,
and the optional backwards-compatibility attribute. Test the full interaction rather than only its initial render,
because many V1/V3 differences appear during hydration and browser updates.

Report reproducible framework defects through GitHub Issues. For implementation help, use the Magewire community
support channels.

## Can Magewire be used with Luma or another theme?

Magewire core is theme-agnostic, but every storefront must load compatible frontend assets and integrate with its
JavaScript and CSP setup. The maintained `magewirephp/magewire-hyva-theme` package provides Hyvä Theme support. Other
themes need an equivalent integration where the core defaults are not sufficient.

Magento's admin area is supported separately through `magewirephp/magewire-admin`.

## Does Hyvä Checkout work with Magewire V3?

Yes. Install `magewirephp/magewire-hyva-checkout` for the Magewire 3 checkout integration. Legacy Hyvä Checkout
components written for Magewire V1 may also need Magewire's backwards-compatibility behavior while they are migrated.

See [Hyvä Checkout Backwards Compatibility](../theming/hyva-checkout-bc.md) for the current opt-in rules and migration
guidance.

## Can Magewire V1 and V3 run simultaneously?

No. They provide different versions of the same framework package and browser runtime. Migrate the installed component
set together, using the compatibility layer only as a temporary bridge for V1-style behavior running on Magewire V3.

## Where can I find the V1 documentation?

The archived V1 documentation is available in the
[`1.13.3` source tree](https://github.com/magewirephp/magewire/tree/1.13.3/docs). It describes an unsupported release and
should not be used as API documentation for Magewire 3.
