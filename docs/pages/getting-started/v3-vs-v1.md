# Magewire V3 vs V1 — what changed

A high-level map of everything built for **Magewire V3** relative to **V1**, organised by area.

V1 was a hand-written Magento runtime modelled on **Livewire v2**. V3 is a **full rewrite**: the
Laravel Livewire **v3** core is ported into Magento (via Portman), the old runtime is replaced by a
formalised **Mechanisms + Features** pipeline, and component state now flows through a
**snapshot**. A first-class **backwards-compatibility layer** keeps V1 components running on the V3
runtime.

> This is a summary of the big shifts, not an exhaustive changelog. For the per-release feature log
> see the [Feature History](releases/feature-history.md); for migrating a component see the
> [Upgrade](upgrade.md) and [Versioning](versioning.md) pages.

---

## TL;DR

| Area | V1 | V3 |
|---|---|---|
| Core | Hand-written, Livewire **v2**-era | Livewire **v3** core ported via **Portman** |
| Architecture | Implicit, monolithic runtime | Formal **Mechanisms** (required) + **Features** (optional) pipeline |
| Boot | Ad-hoc | A **runtime** state machine with request **modes** (preceding/subsequent) |
| Component → block | Hardcoded `magewire` argument | Pluggable **Component Resolvers** |
| State transport | `serverMemo` (v2 payload) | **Snapshot** (`data` + `memo` + `checksum`) with **synthesizers** |
| Templates | Plain `.phtml` | **Template compiler**: `@` directives, fragments, Blade-like echo |
| Events | `emit*()` + `$listeners` | `dispatch()` + `#[On]` |
| Messages | `dispatchSuccessMessage()` … | `magewireNotifications()` / `magewireFlashMessages()` |
| JavaScript | Custom | **Unmodified Livewire bundle** + `MagewireUtilities` / `MagewireAddons` |
| PHP | < 8.2 supported | **8.2+** required |
| Docs | In-repo | Dedicated **MkDocs** site |

---

## 1. Foundation & architecture

- **Livewire v3 core, ported.** V3 brings the upstream Livewire v3 PHP core into Magento through
  **Portman**, so behaviour and concepts align with the wider Livewire ecosystem and upstream fixes
  can be re-adopted. V1 was a bespoke reimplementation of v2 ideas.
- **Mechanisms & Features pipeline.** The runtime is now split into **Mechanisms** (the
  non-negotiable core steps — `ResolveComponents`, `HandleComponents`, `HandleRequests`,
  `FrontendAssets`, …) and **Features** (optional, swappable capabilities). Both are area-scoped DI
  registrations with sort orders. V1 had no such separation.
- **Runtime state machine.** A request-scoped runtime boots Magewire once per request, tracks a
  **state** (`UNINITIALIZED → SETUP → BOOTING → BOOTED`) and a **mode** (`PRECEDING` page render vs
  `SUBSEQUENT` update). Mechanisms key off the mode (e.g. page-less block fetching on updates).
- **Component Resolvers.** *How* a Magento block becomes a component is now pluggable. The
  `LayoutResolver` handles the standard layout-XML case; custom resolvers cover widgets, dynamic
  blocks, Flakes, etc. V1 bound components through a fixed `magewire` block argument only.
- **Layout decoration for dynamic blocks.** On an update, V3 decorates the layout instance so a
  single block can be rebuilt by handle **without a page body** — enabling dynamically loaded /
  re-rendered components that V1 couldn't cleanly express.

## 2. State & the wire

- **Snapshot, not serverMemo.** Component state travels as a **snapshot** — `data` (public
  properties), `memo` (reconstruction metadata: name, id, resolver accessor, layout handles, feature
  flags) and a **checksum** that's verified on every update to reject tampering.
- **Synthesizers.** Non-scalar property values are dehydrated/hydrated by **synthesizers** (arrays,
  `\stdClass`, backed enums, and Magento's `\Magento\Framework\DataObject`). Custom synths register
  via DI. V1 had a much narrower, less formal property serialisation.

## 3. Templates

- **Template compiler.** `.phtml` templates are compiled, enabling simplified syntax that expands to
  PHP at compile time. Templates recompile when the file changes.
- **`@` directives.** Author shorthands that compile into the underlying calls.
- **Blade-like echo** *(3.1.0)*. `{{ }}` (escaped) and `{!! !!}` (raw) echo syntax in templates.
- **Fragments.** Mark a region of a template so modifiers can alter its output — e.g. making inline
  scripts CSP-compliant — via the `fragment()` utility. New in V3.

## 4. Component PHP API

| Concern | V1 | V3 |
|---|---|---|
| Dispatch event | `emit()`, `emitUp()`, `emitSelf()`, `emitTo()`, `emitToRefresh()` | `dispatch()` with `->up()` / `->self()` / `->to()` |
| Listen | `protected $listeners = [...]` | `#[On('event')]` attribute (listeners array still BC-supported) |
| All public props | `getPublicProperties()` | `all()` |
| Component id | public `$id` | `id()` / `getId()` |
| Skip render | `canRender()` | `skipRender()` |
| Switch template | `switchTemplate()` | template resolution / render control |
| Browser event | `dispatchBrowserEvent()` | unified `dispatch()` |
| Errors/validation | `error()`, `getErrors()`, `hasErrors()`, `clearErrors()` | reworked (the upstream `#[Validate]` validation feature is **not active** in Magewire today) |
| Messages | `dispatchSuccessMessage()` / `dispatchErrorMessage()` … | `magewireFlashMessages()->make()->asSuccess()` and `magewireNotifications()->make()` |

The V1 method names above are preserved by the BC layer's trait so existing components keep working.

## 5. Directives & JavaScript

- **JS is an unmodified Livewire bundle.** V3 serves Livewire's JS as a Magento static asset, kept
  untouched so upstream upgrades are a file swap. V1 shipped custom JS.
- **Utilities & Addons.** `window.MagewireUtilities` (`dom`, `loader`, `str`, `cookie`) and
  `window.MagewireAddons` (the notifier) are registerable, layout-driven extension points. New in V3.
- **`wire:*` default changes (v2 → v3):**

| V1 / v2 | V3 | Behaviour |
|---|---|---|
| `wire:model` | `wire:model.live` | instant sync |
| `wire:model.defer` | `wire:model` | deferred (now the default) |
| `wire:model.lazy` | `wire:model.blur` | on blur |
| `$wire.entangle('p')` (live) | `$wire.entangle('p').live` | live is now opt-in |

- **Renamed JS hooks** — `component.initialized → component.init`, `message.sent/received → commit`,
  etc. (the BC JS shim re-fires the old names for BC-enabled components).

## 6. New features in V3

Optional capabilities that didn't exist (or weren't formalised) in V1:

- **Notifications** — fluent toast API (`magewireNotifications()`).
- **Magento Flash Messages** — typed messages (`error`/`warning`/`notice`/`success`) rendered in
  Magento's message area.
- **Rate limiting** — configurable per-component request throttling.
- **Loaders / offline states** — first-class loading and offline UX (reworked from V1).
- **Nesting components** — formal parent/child support.
- **Flakes** — lightweight components resolved by layout handle (secondary resolver).
- **View Model utilities** — `utils()` surface (`magewire`, `security`, `env`, `csp`, `fragment`,
  `layout`, `template`) auto-bound to every Magewire block.
- **Exception handling** — preceding vs subsequent handling, an error placeholder template, custom
  handlers via DI, and an `exception()` component hook.
- **Component Hooks** — a broad `on()` / `trigger()` lifecycle pipeline for extending the framework.
- **CSP compliance** — nonce/fragment support for payment-grade Content-Security-Policy.

## 7. Magento integration

- **Observer events** — every lifecycle event is re-emitted as a Magento observer event
  (`magewire_on_*`), so you can react with a plain `events.xml` observer.
- **Layout containers** — a documented container/block tree for injecting JS, Alpine data, UI
  components, and feature bridges from a theme.
- **Component layout context** — components expose `magewireBlock()`, `magewireResolver()`,
  `magewireLayoutLifecycle()`.
- **Admin package** — a dedicated `magewire-admin` package brings components to the Magento admin
  (head-injection strategy, admin resolver/route).
- **Structured block arguments** — `magewire.*` (→ properties), `magewire:{group}:{key}` (→ grouped,
  e.g. `mount`), and reserved `magewire:resolver` / `magewire:alias`.

## 8. Tooling, platform & docs

- **Portman** — the tool that ports upstream libraries (Livewire) into Magento and keeps them in
  sync.
- **PHP 8.2+** — support for PHP below 8.2 was dropped.
- **Dedicated documentation** — a GitHub-hosted MkDocs site replaces in-repo docs.

## 9. Backwards compatibility

V3 ships a **BC layer** so V1 components run on the V3 runtime without a rewrite:

- Opt in per component with `#[HandleBackwardsCompatibility]` (or out with `enabled: false`).
- A PHP trait keeps the deprecated V1 APIs (`emit*`, `getPublicProperties()`, public `$id`, error
  helpers, `dispatch*Message()`).
- A JS shim rewrites `wire:*` directives, restores live-by-default `entangle`, and re-fires renamed
  hook names for BC-enabled components.
- Disable the whole subsystem via DI once everything is migrated.

---

## Where to read more

- Architecture: Runtime, Mechanisms (Resolvers, HandleComponents, HandleRequests, FrontendAssets),
  Layout, Features, Component Hooks, Observer Events, Synthesizers.
- Essentials: Components, View Model & Utilities, Backwards Compatibility.
- Features: Notifications, Rate Limiting, Redirects, Template Directives.
- Getting Started: Feature History (per-release log), Upgrade (V1 → V3 checklist).
