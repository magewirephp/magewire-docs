# Layout

Magewire is a large framework with many options and features. Still, the layout stays flexible — there is a documented extension point for injecting JavaScript, UI components, Alpine data, and every other piece of frontend wiring Magewire ships.

It's impossible to explain everything, and many parts are self-explanatory or include clear comments in the layout files. The sections below cover the containers and blocks you are most likely to target from a theme or a feature module.

The canonical source is `src/view/base/layout/default.xml` — the tree below mirrors it. Frontend and admin layouts add a small number of page-level moves on top (documented at the end).

## Container tree

```
head.additional
└── magewire.css                              ← CSS for wire:* attributes (loading / cloak states)

after.body.start
└── magewire.priority                         ← early JS, runs right after <body> opens
    └── magewire.object-proxy   (frontend)    ← window.Magewire stub so inline snippets can queue work

magewire (root block — Magewirephp_Magewire::root.phtml)
├── magewire.global (block — js/magewire/global.phtml)
│   ├── magewire.global.before (container)
│   │   ├── magewire.alpinejs.load            ← Alpine JS <script> tag goes here (empty; theme fills it)
│   │   ├── magewire.alpinejs (container)
│   │   │   └── magewire.alpinejs.magewire    ← Alpine global functions, $wire
│   │   └── magewire.alpinejs.components (container)
│   │       ├── magewire.alpinejs.components.magewire-notifier        ← core notifier Alpine.data
│   │       └── magewire.alpinejs.components.magewire-script (frontend) ← boots Magewire's JS runtime
│   ├── magewire.utilities (block)            ← window.MagewireUtilities
│   │   ├── magewire.utilities.dom
│   │   ├── magewire.utilities.loader
│   │   ├── magewire.utilities.str
│   │   ├── magewire.utilities.cookie
│   │   └── magewire.utilities.after          ← custom utilities render after core
│   ├── magewire.addons (block)               ← window.MagewireAddons
│   │   ├── magewire.addons.notifier          ← core notifier addon
│   │   └── magewire.addons.after             ← custom addons render after core
│   └── magewire.global.after (container)
├── magewire.before (container)               ← theme-owned directives / UI components
│   ├── magewire.alpinejs.directives          ← custom Alpine directives
│   ├── magewire.ui-components (container)
│   │   └── magewire.ui-components.notifier    ← core notifier UI component
│   │       ├── …notifier.notification.before
│   │       └── …notifier.notification.after
│   │           └── …notifier.activity-state
│   │               └── …notifier.activity-state.loader-icon   ← spinner
│   └── magewire.alpinejs.after               ← Alpine code rendered AFTER Magewire's
├── magewire.before.internal (container)      ← before core internals; holds magewire.state.enabled (debug)
├── magewire.internal (block)                 ← non-overridable framework internals
│   └── magewire.internal.backwards-compatibility   ← v1 BC shims only
├── magewire.directives (block)               ← wire:* / mage-* directives
│   ├── magewire.directives.select
│   ├── magewire.directives.mage-notify
│   └── magewire.directives.mage-throttle
├── magewire.features (block)                 ← Feature bridge scripts
│   ├── magewire.features.support-magewire-loaders
│   └── magewire.features.support-magewire-rate-limiting
├── magewire.after.internal (container)       ← runs after core internal block (rare)
├── magewire.disabled (container)             ← ONLY rendered when Magewire is disabled
│   └── magewire.state.disabled               ← debug-only disabled notice
├── magewire.after (container)                ← last-to-render theme content
└── magewire.legacy (container)
    └── magewire.plugin.scripts               ← pre-v3 plugin compatibility
```

The base layout also defines two blocks **outside** the `magewire` root subtree — `magewire.css` (in `head.additional`) and `magewire.priority` (in `after.body.start`). They are not moved with the root and stay where they render best: CSS in the head, priority JS right after the body opens.

Frontend layout (`src/view/frontend/layout/default.xml`) adds on top:

- `<move element="magewire" destination="before.body.end"/>` — moves the whole `magewire` root subtree to the end of `<body>` (`magewire.css` and `magewire.priority` stay put).
- `magewire.alpinejs.components.magewire-script` inside `magewire.alpinejs.components` — the Alpine component that boots Magewire's JS runtime.
- `magewire.object-proxy` as a child of `magewire.priority` — early global object so inline snippets can queue work against `window.Magewire` before the runtime boots.

Admin layout (`magewire-admin` package) replaces the body-end move with a head-injection strategy — see [Admin → How it works](../../admin/how-it-works.md).

## Containers

| Container / block                    | Type      | Description |
|--------------------------------------|-----------|-------------|
| `magewire.css`                       | block     | Lives in `head.additional`. Renders the CSS for `wire:*` attributes (loading / cloak states). Outside the `magewire` root subtree. |
| `magewire.priority`                  | block     | Lives in `after.body.start`. Early JS that must run right after `<body>` opens. Hosts `magewire.object-proxy` on the frontend. Outside the `magewire` root subtree. |
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
| `magewire.before.internal`           | container | Before Magewire's internal machinery. Reserved for framework use; ships the debug-only `magewire.state.enabled` notice (`ifconfig dev/magewire/debug/enable`). |
| `magewire.internal`                  | block     | Non-overridable core. Deliberately a block, not a container, so arbitrary injection is impossible. Inject via `magewire.after.internal` instead. |
| `magewire.internal.backwards-compatibility` | container | v1 BC shims only. Reserved. |
| `magewire.directives`                | block     | Magewire's own `wire:*` / `mage-*` directives (select, mage-notify, mage-throttle). |
| `magewire.features`                  | block     | Feature-side bridge scripts (loaders, rate-limiting, etc.). One child per Feature by convention. |
| `magewire.after.internal`            | container | After the internal block. Use when you must interleave with core internals. |
| `magewire.disabled`                  | container | Rendered ONLY when Magewire is disabled site-wide — surface a fallback or a warning here. Ships the debug-only `magewire.state.disabled` notice. |
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
| Style `wire:*` loading / cloak states | `magewire.css` |
| Run JS immediately after `<body>` opens | `magewire.priority` |

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

`magewire.global`, `magewire.internal`, `magewire.directives`, `magewire.features`, `magewire.utilities`, and `magewire.addons` are **blocks**, not containers — each has a template that renders a scaffold around its children. Two practical consequences:

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

## Dynamic, page-less block loading

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Everything above describes layout XML at rest — the container tree as it renders on a normal page load. This last section covers what happens to the **layout instance itself** during a Magewire update, and why it can hand back a block that was never attached to a `<body>`.

### The problem

On a normal page render, Magento builds a single global `Layout` singleton, bound to the current route. Every block hangs off the page body root, and the generator pool knows how to build heads, bodies, containers and blocks alike.

A Magewire update (`/magewire/update`) is **not** a page render. There is no route, no `<body>`, no head. Yet the [`LayoutResolver`](mechanisms/resolvers.md) still has to replay a component's stored layout handles and pull a *single* block back out by name to rebuild the component (see [Resolvers → reconstruction](mechanisms/resolvers.md#the-built-in-layoutresolver)). A block normally needs a page as its root parent to bind to — and on an XHR there isn't one.

### Decorating the layout instance

Magewire solves this by **decorating the layout instance at runtime**, but only on subsequent (XHR) requests. `ResolveComponents::boot()` checks the runtime mode first:

```php
// Magewirephp\Magewire\Mechanisms\ResolveComponents\ResolveComponents
if ($this->magewireServiceProvider->runtime()->mode()->isSubsequent()) {
    $this->layoutManager->decorator()->decorateForPagelessBlockFetching($this->layoutManager->singleton());
}
```

On the **initial** page load nothing is decorated — the layout behaves exactly like stock Magento. The decoration only applies during an update roundtrip, where page-less fetching is actually needed.

`MagewireLayoutDecorator::decorateForPagelessBlockFetching()` swaps two pieces of the layout instance:

```php
public function decorateForPagelessBlockFetching(LayoutInterface $layout): LayoutInterface
{
    if ($layout instanceof Layout) {
        $builder = $this->dynamicLayoutBuilder->newInstance(['layout' => $layout]);

        // Custom generator pool — only blocks and containers are allowed to generate.
        $layout->setGeneratorPool($this->generatorPool);
        // Custom builder — limits rebuilds for repetitive layouts.
        $layout->setBuilder($builder);
    }

    return $layout;
}
```

**1. A restricted generator pool.** The custom `GeneratorPool` limits the layout's generators to just `block` and `container` — head, body, and the other page-structure generators are dropped, because there is no page to structure. More importantly, it replaces Magento's `ScheduledStructure\Helper` with a Magewire variant that **emulates a missing root**: when a block's declared parent element doesn't exist (because no page body was ever built), the helper fabricates a fictional container element so the child still has something to bind to. This is the mechanism that lets a block resolve "without being attached to a page body".

**2. A caching builder.** The custom `DynamicLayoutBuilder` hashes the sorted set of active handles and caches the built layout per hash. Building the same handle set twice in one request returns the cached instance instead of re-running `generateXml()` / `generateElements()` — preventing the repetitive (and potentially recursive) rebuilds that page-less fetching would otherwise trigger. `rebuild()` / `reset()` force a fresh build when you genuinely need one.

### How a resolver consumes it

With the layout decorated, the `LayoutResolver` recovers a block by replaying its stored handles and reading straight from the (now page-less) block tree:

```php
protected function generateBlocks(array $handles): array
{
    $layout = $this->layoutManager->singleton();
    $layout->getUpdate()->addHandle($handles);

    return $layout->getAllBlocks(); // keyed by name-in-layout — pick the one you need
}
```

The handles came from the snapshot memo stashed on `dehydrate`; the block name (or alias) selects the single block to reconstruct.

### Two layout sources

The `LayoutManager` is the entry point for both layout flavours, and exposes the decorator:

| Method | Returns |
|---|---|
| `singleton()` | The global layout singleton — decorated in place during reconstruction. |
| `factory()` | A `LayoutFactory` for building a **fresh, isolated** layout instance. |
| `decorator()` | The `LayoutDecorator` used to enable page-less fetching on either of the above. |
| `lifecycle(string $name = 'magewire')` | The named `LayoutLifecycle` tracker. |

Most reconstruction decorates the shared singleton. Some features need an isolated layout instead — `FlakeFactory`, for example, decorates a brand-new layout (`factory()->create()`) so it can fetch flake blocks without touching the page's own layout state.

### Swapping the decorator

The decorator is bound through a DI preference, so it is replaceable:

```xml title="src/etc/di.xml"
<preference for="Magewirephp\Magewire\Mechanisms\ResolveComponents\Layout\LayoutDecorator"
            type="Magewirephp\Magewire\Mechanisms\ResolveComponents\Layout\MagewireLayoutDecorator"/>
```

!!! warning "Framework internals"
    This decoration is core machinery — you rarely touch it directly. Override the `LayoutDecorator` preference only if you have a genuine reason to change *how* page-less blocks are assembled on an XHR. For normal work (adding directives, features, Alpine wiring) stick to the layout XML containers documented above.
