# Layout

Magewire is a large framework with many options and features. Still, the layout stays flexible — there is a documented extension point for injecting JavaScript, UI components, Alpine data, and every other piece of frontend wiring Magewire ships.

It's impossible to explain everything, and many parts are self-explanatory or include clear comments in the layout files. The sections below cover the containers and blocks you are most likely to target from a theme or a feature module.

The canonical source is `src/view/base/layout/default.xml` — the tree below mirrors it. Frontend and admin layouts add a small number of page-level moves on top (documented at the end).

## Container tree

```
magewire (root block — Magewirephp_Magewire::root.phtml)
├── magewire.global (block)
│   ├── magewire.global.before (container)
│   │   ├── magewire.alpinejs.load            ← Alpine JS <script> tag goes here
│   │   ├── magewire.alpinejs                 ← Alpine global functions, $wire
│   │   └── magewire.alpinejs.components      ← Alpine.data(...) registrations
│   ├── magewire.utilities (block)            ← MagewireUtilities.register(...)
│   │   └── magewire.utilities.after          ← custom utilities render after core
│   ├── magewire.addons (block)               ← MagewireAddons.register(...)
│   │   └── magewire.addons.after             ← custom addons render after core
│   └── magewire.global.after
├── magewire.before (container)               ← theme-owned directives / UI components
│   ├── magewire.alpinejs.directives          ← custom Alpine directives
│   ├── magewire.ui-components                ← notifier, dialogs, drawers, etc.
│   └── magewire.alpinejs.after               ← Alpine code rendered AFTER Magewire's
├── magewire.before.internal                  ← runs before core internal blocks (rare)
├── magewire.internal (block)                 ← non-overridable framework internals
│   └── magewire.internal.backwards-compatibility   ← v1 BC shims only
├── magewire.directives (block)               ← wire:* directives (select, mage-notify, mage-throttle)
├── magewire.features (block)                 ← Feature bridge scripts
├── magewire.after.internal                   ← runs after core internal blocks (rare)
├── magewire.disabled (container)             ← ONLY rendered when Magewire is disabled
├── magewire.after (container)                ← last-to-render theme content
└── magewire.legacy (container)
    └── magewire.plugin.scripts               ← pre-v3 plugin compatibility
```

Frontend layout (`src/view/frontend/layout/default.xml`) adds on top:

- `<move element="magewire" destination="before.body.end"/>` — moves the whole subtree to the end of `<body>`.
- `magewire.alpinejs.components.magewire-script` inside `magewire.alpinejs.components` — the Alpine component that boots Magewire's JS runtime.
- `magewire.object-proxy` inside `after.body.start` — early global object so inline snippets can queue work against `window.Magewire`.

Admin layout (`magewire-admin` package) replaces the body-end move with a head-injection strategy — see [Admin → How it works](../../admin/how-it-works.md).

## Containers

| Container / block                    | Type      | Description |
|--------------------------------------|-----------|-------------|
| `magewire`                           | block     | Root; wraps every Magewire-owned output. Do not replace its template — override children instead. |
| `magewire.global`                    | block     | Global setup pass — runs once per page, before any per-feature wiring. |
| `magewire.global.before`             | container | First region inside `magewire.global`. Used by the Alpine load, Alpine init, utilities, addons. |
| `magewire.global.after`              | container | After-hook inside `magewire.global`. Empty by default — safe place for page-level hooks that must run after utilities / addons are registered. |
| `magewire.alpinejs.load`             | container | Where Alpine's own `<script>` tag is rendered. Reorder or swap the Alpine bundle here. |
| `magewire.alpinejs`                  | container | Holds the block that defines Magewire's Alpine global (`Alpine.data`, `Alpine.store`). Targeted by themes that add global Alpine helpers. |
| `magewire.alpinejs.components`       | container | `Alpine.data(...)` registrations. Each child block renders an `<script>` calling `Alpine.data`. |
| `magewire.before`                    | container | Everything that must precede Magewire's own directives/features. Theme-owned by convention. |
| `magewire.alpinejs.directives`       | container | Custom `x-*` directive registrations. |
| `magewire.ui-components`             | container | UI Alpine components — the core notifier lives here; theme overrides and additions too. |
| `magewire.alpinejs.after`            | container | Alpine code that must load AFTER Magewire's Alpine wiring. |
| `magewire.before.internal`           | container | Before Magewire's internal machinery. Reserved for framework use. |
| `magewire.internal`                  | block     | Non-overridable core. Deliberately a block, not a container, so arbitrary injection is impossible. Inject via `magewire.after.internal` instead. |
| `magewire.internal.backwards-compatibility` | container | v1 BC shims only. Reserved. |
| `magewire.directives`                | block     | Magewire's own `wire:*` / `mage-*` directives (select, mage-notify, mage-throttle). |
| `magewire.features`                  | block     | Feature-side bridge scripts (loaders, rate-limiting, etc.). One child per Feature by convention. |
| `magewire.after.internal`            | container | After the internal block. Use when you must interleave with core internals. |
| `magewire.disabled`                  | container | Rendered ONLY when Magewire is disabled site-wide — surface a fallback or a warning here. |
| `magewire.after`                     | container | Last-to-render Magewire content. Theme-owned; safe default for theme-final output. |
| `magewire.utilities`                 | block     | Loads `window.MagewireUtilities` and registers core utilities (dom, loader, str, cookie). |
| `magewire.utilities.after`           | container | Inject custom utilities so they register after the core ones. |
| `magewire.addons`                    | block     | Loads `window.MagewireAddons` and registers core addons (notifier). |
| `magewire.addons.after`              | container | Inject custom addons so they register after the core ones. |
| `magewire.legacy`                    | container | BC shelf for v1 block/container names. |
| `magewire.plugin.scripts`            | container | Pre-v3 plugin compatibility target. |

## `<referenceContainer>` vs `<referenceBlock>`

```xml
<!-- Add a sibling block inside a container. Original children keep rendering. -->
<referenceContainer name="magewire.features">
    <block name="magewire.features.my-bridge"
           template="MyVendor_MyModule::magewire-features/my-bridge.phtml"/>
</referenceContainer>

<!-- Replace an existing block's template. Original template is gone. -->
<referenceBlock name="magewire.features.support-magewire-loaders"
                template="MyVendor_MyModule::override-loaders.phtml"/>
```

Default to `<referenceContainer>`. Reach for `<referenceBlock>` only when you deliberately want to swap the template of a named block (for example, overriding the admin rate-limiting template with an admin-styled variant).

## Ordering within a container

Magento layout XML honours `after=` / `before=` among siblings. For deterministic ordering inside a container:

```xml
<block name="magewire.features.my-bridge"
       template="..."
       after="magewire.features.support-magewire-loaders"/>
```

Do not rely on file load order — that depends on module sequence and is brittle.

## Which container to target

| Goal | Target |
|---|---|
| Reorder or swap the Alpine bundle | `magewire.alpinejs.load` |
| Register a global JS helper (Magewire consumers) | `magewire.utilities.after` |
| Register an independent addon (e.g. notifier replacement) | `magewire.addons.after` |
| Add an `Alpine.data(...)` component | `magewire.alpinejs.components` |
| Add a custom Alpine directive (`x-*`) | `magewire.alpinejs.directives` |
| Add a Magewire-level `wire:*` / `mage-*` directive | `magewire.directives` |
| Bridge a Feature's JS counterpart | `magewire.features` |
| Inject theme-final content | `magewire.after` |
| Render a fallback when Magewire is disabled | `magewire.disabled` |

## Directories & Templates

Magewire's `src/view/base/templates/` directory is organised by the library the template targets — the path tells you what the template does before you open it.

### Top-level directories

| Directory | Purpose |
|---|---|
| `js/` | Templates whose primary payload is a `<script>` block. |
| `magewire/` | PHTML UI templates (components and shared pieces) with negligible JS. |
| `magewire-features/` | One subdirectory per registered Feature — bridge PHTML paired with `magewire.features.*` blocks. |

### Under `js/`

| Directory | Purpose |
|---|---|
| `js/alpinejs/` | Alpine-related templates. |
| `js/alpinejs/components/` | Alpine `.data(...)` registrations — one file per component. |
| `js/alpinejs/directives/` | Alpine `x-*` directive registrations. |
| `js/magewire/` | Magewire runtime templates. |
| `js/magewire/addons/` | One file per `MagewireAddons.register(...)` call (the notifier lives here). |
| `js/magewire/utilities/` | One file per `MagewireUtilities.register(...)` call (dom, loader, str, cookie). |
| `js/magewire/directives/` | Magewire-level directive registrations (select, mage-notify, mage-throttle). |
| `js/magewire/internal/` | Non-overridable internals — do not add here from a module. |

### Under `magewire/`

| Directory | Purpose |
|---|---|
| `magewire/ui-components/` | Alpine-driven UI components (notifier, notifier activity state, …). |
| `magewire/utils/` | Shared PHTML snippets consumed by other templates (icons, spinners). |
| `magewire/flakes/` | Flake templates — see [Magewire Flakes](../../features/magewire-flakes.md). |

### Under `magewire-features/`

Each Feature gets its own kebab-cased subdirectory matching its container name. For example:

```
magewire-features/
├── support-magewire-loaders/
│   └── support-magewire-loaders.phtml
└── support-magewire-rate-limiting/
    └── support-magewire-rate-limiting.phtml
```

Pair a child block under `magewire.features` with a template in `Vendor_Module::magewire-features/<kebab-name>/<kebab-name>.phtml`. The admin rate-limiting override in `magewire-admin` follows the same convention — reuse it in your own theme modules.

!!! tip "Building something custom or making a contribution? Always examine the folder and file structure closely to ensure you're in the right location."

## Blocks that look like containers

`magewire.internal`, `magewire.directives`, `magewire.features`, `magewire.utilities`, and `magewire.addons` are **blocks**, not containers — each has a template that renders a scaffold around its children. Two practical consequences:

- You cannot `<referenceContainer name="magewire.features">` and expect it to work in every context — Magento is picky about container vs. block reference types. `<referenceBlock>` works for both when you only need to add children, but prefer the correct tag for the target.
- To completely swap the scaffold (e.g. a different wrapper for all directives), override the template with `<referenceBlock name="magewire.directives" template="..."/>`. Rare; only do this when the parent's markup genuinely needs replacing.

## Off-limits from a theme

- `magewire` root block itself — do not replace its template.
- `magewire.internal` and anything directly under it (except the BC sub-container) — reserved for core.
- `magewire.before.internal` / `magewire.after.internal` — used only when the framework's own internal ordering requires it.

If a container you need doesn't exist, add one in `default_{theme}.xml` as a child of an existing container rather than repurposing a reserved one.

## Page-specific vs global overrides

- `default_{theme}.xml` — applies on every page where the theme is active. Use for load-order fixes, global Feature bridges, BC shims.
- `{route}_{controller}_{action}.xml` — applies on one route only. Use for page-scoped Features (for example, Hyvä Checkout's BC feature is activated only on `hyva_checkout_index_index`).

Smaller scope is cheaper — page-specific handles avoid paying for the block on every page.
