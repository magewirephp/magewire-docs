# Best Practices

Magewire does not require a particular application-module structure, but predictable locations make components easier
to discover and keep framework extensions separate from application behavior.

## Recommended module structure

For a typical storefront feature, keep PHP components below `Magewire/` and their templates below
`view/{area}/templates/magewire/`:

```text
Vendor/Module/
├── Magewire/
│   ├── Cart/
│   │   ├── Coupon.php
│   │   └── Summary.php
│   ├── Features/
│   │   └── SupportWishlistPreview/
│   └── Mechanisms/
│       └── ResolveComponents/
├── etc/
│   └── frontend/
│       └── di.xml
└── view/
    └── frontend/
        ├── layout/
        │   └── checkout_cart_index.xml
        └── templates/
            └── magewire/
                └── cart/
                    ├── coupon.phtml
                    └── summary.phtml
```

Mirror component namespaces in the template path where practical. A component named
`Vendor\Module\Magewire\Cart\Coupon` is easy to find next to
`Vendor_Module::magewire/cart/coupon.phtml`.

Use `frontend`, `adminhtml`, or `base` deliberately. Put application-specific templates and DI configuration in the
area that uses them. Reserve `view/base` and global `etc/di.xml` for behavior that genuinely has to run in every area.

## Components, Features, and Mechanisms

Most application code only needs component classes directly below `Magewire/`:

- A **component** owns UI state and actions for one rendered block.
- A **Feature** hooks into the component lifecycle to add optional behavior across multiple components.
- A **Mechanism** owns a lower-level part of the runtime, such as component resolution or request handling.

Do not introduce a Feature or Mechanism merely to share application logic. Put reusable business behavior in an
ordinary Magento service and inject that service into the component. Extend Magewire internals only when the behavior
must participate in framework lifecycle or infrastructure.

Follow the current Magewire source namespaces when building framework extensions. V1 examples and older V3 releases
may refer to Feature classes that have since moved into `Magewire/Mechanisms`.

## JavaScript integration

Keep JavaScript owned by a Magewire extension close to the responsibility it implements:

```text
view/{area}/templates/js/magewire/features/{feature-name}/
view/{area}/templates/js/magewire/directives/{directive-name}/
```

Register those templates through layout XML instead of embedding a copy of Magewire's internal scripts in an
application template. Use a [CSP-aware script fragment](../concepts/fragments.md) for inline JavaScript, wait for
`magewire:init` before accessing the Magewire runtime, and clean up global hooks or event listeners when their owner is
removed.

Prefer Alpine data components for local browser-only state. Add a custom Magewire directive only when the behavior
needs to integrate with Magewire's directive lifecycle, and add a Feature only when it needs server-side lifecycle or
response effects as well.

## Component boundaries

- Keep one stable root element in every component template.
- Use a normal Magento child block when the child does not need independent reactive state.
- Use a nested Magewire component when the child needs its own snapshot, actions, or lifecycle.
- Add stable `wire:key` values to repeated or reorderable elements.
- Keep public component properties serializable and free of secrets.
- Validate and authorize every public action, even when the button that calls it is conditionally hidden.

## Reusing component classes

Magento object arguments are shared by default. When the same component class is bound to more than one block, set
`shared="false"` on each `magewire` object argument so every block receives an independent instance:

```xml
<argument name="magewire" xsi:type="object" shared="false">
    Vendor\Module\Magewire\Cart\Summary
</argument>
```

For more detail, see [Components](../essentials/components.md), [Nesting Components](../essentials/nesting-components.md),
[Security](security.md), and the [Architecture](architecture/index.md) section.
