---
title: Magewire 3 - Finally! #5
authors:
    - willem
date: 2026-04-23
tags: [V3, release]
---

!!! warning "Historical release post"
    This post records the V3 release announcement. Some release-day descriptions changed before Magewire 3.6.
    Follow the linked documentation for current behavior, especially for Alpine loading, Flakes, synthesizers, and
    Hyvä Checkout backwards compatibility.

True, this has taken a while, but nevertheless it is now finally happening. Who would have thought.

Even though I can think of more than enough reasons as an excuse for the late release of the first official version of Magewire V3,
that doesn't seem necessary for an open source project.

I think it's more appropriate to express my gratitude to the sponsors who stuck it out until the end and thereby indirectly gave me their confidence.
So with that, let me at least already thank Vendic and Hyvä, with the positive hope that it won't stop here,
and that this might even be the moment for others to start and/or continue supporting me and/or this project.

## So, V3 is finally real

V1 was an experiment. V2 was skipped entirely so we could align versioning with Livewire. V3 is the version I actually wanted to ship from day one, an honest, full port of Livewire V3, wearing Magento clothes but thinking like a modern reactive framework.

Most of what you already read in the [beta blog](beta-release.md) made it in. On top of that, a lot has been hardened, polished, and refactored. This post walks through the lineup as it looks today, on release day, so you know what you're getting when you run `composer require magewirephp/magewire`.

## Built on Livewire, not just inspired by it

Magewire isn't a reimplementation with a Magento flavour. The PHP core is *ported* from Livewire V3 using a small tool
called **Portman**, which rewrites Laravel-isms into Magento-isms while preserving the original code shape. The
JavaScript runtime is based on pinned Livewire and Alpine sources with Magewire-specific patches, then served as a
Magento static asset.

What that buys you is enormous. Every time Livewire ships a fix or a feature, we can adopt it in an afternoon. Remember the [critical security patch in July](https://github.com/livewire/livewire/security/advisories/GHSA-29cq-5w36-x7w3)? Ten minutes to port. A framework this small should never be a one-maintainer knowledge silo, and now it isn't.
We inherit an entire ecosystem of eyes, fingers, and documentation.

## The Livewire goodies you now get for free

If you only used V1, this is probably the biggest jump:

- **`$wire`**: the reactive proxy on every component. Read any public property, call any public method, subscribe to any event, all from Alpine or inline JS.
- **`#[On('event-name')]`**: PHP attributes replace the old `$listeners` array. Less boilerplate, better IDE support.
- **Entangle with deferred default**: `$wire.entangle('open')` gives you an Alpine-friendly two-way proxy that no longer floods the server on every keystroke. Add `.live` when you actually want live.
- **`wire:model` is deferred by default**: same story, different directive. Use `.live`, `.blur`, or `.live.debounce.300ms` depending on what you need.
- **Bundled Alpine, with only one active copy**: Magewire ships the CSP build of Alpine inside its JS bundle. Do not
  remove a theme's Alpine loader globally. Install the appropriate compatibility package and let it select one
  compatible Alpine runtime per page.
- **Streaming**: `wire:stream` works. A Magento output-buffering layer made this harder than it should have been, but we got there.
- **Modern morphing, modern commit hooks**: the frontend uses Livewire's current morph algorithm with all its bug fixes. Every request goes through the `commit` hook pipeline, so you can intercept, retry, or observe without hacks.
- **Lifecycle hooks that read like Laravel**: `boot`, `booted`, `mount`, `hydrate`, `updating`/`updated`, `rendering`/`rendered`, `dehydrate`, `exception`. Plus per-property variants (`updatedFirstName`, `hydrateCart`).

These capabilities originate in Livewire V3, but Magewire ports a selected subset into Magento. Do not assume an
upstream Livewire API exists unless the current Magewire documentation or source registers it.

## What Magewire adds on top

Some problems are uniquely Magento-shaped, and Magewire takes them seriously.

- **Fragments.** An explicitly-scoped slice of output that Magewire can validate, hash, and decorate before it reaches
  the browser. Script fragments provide CSP handling and receive the built-in developer annotation.
- **Magewire Flakes.** Flakes remain experimental in Magewire 3.6. The release-day tag syntax shown in earlier versions
  is obsolete, and the current source contains an unresolved fragment registration. Do not use Flakes in production.
- **Template Directives.** The supported `@auth`, `@guest`, `@translate`, `@child`, `@json`,
  `@escapeUrl`, and fragment directives compile to PHP. `@ucfirst` is not a registered Magewire 3.6 directive.
- **Rate limiting.** Both sides: client-side via `wire:mage:throttle`, and a server-side cache-driven limiter configured from the admin. Use one, use both, use neither. The cache driver is swappable.
- **Observer Events.** A fixed map of Magewire lifecycle events is re-emitted as Magento observer events prefixed
  `magewire_on_*`. Custom hook names are not bridged automatically.
- **A proper notifier.** Fluent API from PHP (`$this->magewireNotifications()->make(...)->asSuccess()`), Alpine-rendered on the frontend, themeable per site. Handles named notifications so you don't stack duplicate toasts.
- **Synthesizers for Magento types.** A DataObject synthesizer is registered, but its Magewire 3.6 array-cast
  implementation does not guarantee a dependable round trip. It does not support arbitrary Magento models. Prefer a
  public array until the DataObject implementation is corrected.
- **Area-scoped DI, finally done right.** Features and Mechanisms register in `etc/frontend/di.xml` or `etc/adminhtml/di.xml`. The storefront and admin can ship genuinely different feature sets without the global-DI circus that plagued V1.

## Reaching the admin

Magewire V1 was storefront-only. V3 isn't. A companion package, `magewirephp/magewire-admin`, ships the admin route, the session check, the Prototype.js collision shim, the Renderer plugin that loads Magewire before RequireJS, everything needed to run Magewire components inside Magento's admin panel.

```
composer require magewirephp/magewire-admin
```

Layout XML is the same as storefront. Lifecycle is the same. Alpine is the same (minus Tailwind, the admin has its own styles). Build a reactive grid, an inline editor, a refund wizard, it just works. You still need to add ACL checks in every action, because any public method is a public endpoint. But that part is on you.

## Under the hood

V3 is a complete architectural rewrite. Three concepts you'll see everywhere in the docs:

- **Mechanisms**: the non-removable backbone: component resolving, snapshot handling, request handling, frontend assets. You extend them; you don't delete them.
- **Features**: smaller lifecycle capabilities. Some are optional, while lifecycle hooks, events, and other core
  Features are required for the documented runtime.
- **Component Hooks**: the primitive behind everything. A class that subscribes to lifecycle events (`mount`, `render`, `dehydrate`, …) with middleware semantics. Almost every Feature is one.

Every custom piece you write, a new resolver, a new synthesizer, a new feature, a theme adapter, plugs into this shape. The boundary between core, theme, and userland is clearer than it has ever been.

## Coming from V1

Magewire includes a targeted backwards-compatibility layer. The attribute enables its documented browser
transformations, but a V1 component still needs end-to-end migration testing:

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class LegacyCart extends \Magewirephp\Magewire\Component { /* ... */ }
```

The BC layer rewrites `wire:model` → `wire:model.live`, re-triggers deprecated event names, proxies `component.data` → `component.$wire`, and a handful of other transforms. You buy time to migrate without rewriting every component on the day you upgrade.

For Hyvä Checkout, add the attribute explicitly to every legacy component. In Magewire 3.6 the core resolver writes a
false default before the companion package checks its container fallback, so automatic opt-in is not reliable.

The full migration checklist lives in the [Upgrade guide](../../pages/getting-started/upgrade.md).

## Give it a spin

That's the tour. Not everything, obviously, the docs cover the rest. But this is the shape of V3, on release day, and I genuinely think it's a better framework than anything I've built before.

```
composer require magewirephp/magewire
```

Try it, break it, open issues, open PRs, send screenshots when you make something cool. Magewire has always been a small, focused project, and it stays alive because people actually use it and actually contribute back.

Thanks for waiting. Now stop reading and go build something reactive.
