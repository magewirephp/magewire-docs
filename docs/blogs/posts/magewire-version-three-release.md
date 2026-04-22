---
title: Magewire 3 - Finally! #5
authors:
    - willem
date: 2026-04-23
tags: [V3, release]
---

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

Magewire isn't a reimplementation with a Magento flavour. The PHP core is *ported* from Livewire V3 using a small tool called **Portman**, which rewrites Laravel-isms into Magento-isms while preserving the original code shape. The JavaScript bundle is an unmodified copy of Livewire's JS, served as a Magento static asset.

What that buys you is enormous. Every time Livewire ships a fix or a feature, we can adopt it in an afternoon. Remember the [critical security patch in July](https://github.com/livewire/livewire/security/advisories/GHSA-29cq-5w36-x7w3)? Ten minutes to port. A framework this small should never be a one-maintainer knowledge silo, and now it isn't.
We inherit an entire ecosystem of eyes, fingers, and documentation.

## The Livewire goodies you now get for free

If you only used V1, this is probably the biggest jump:

- **`$wire`** — the reactive proxy on every component. Read any public property, call any public method, subscribe to any event, all from Alpine or inline JS.
- **`#[On('event-name')]`** — PHP attributes replace the old `$listeners` array. Less boilerplate, better IDE support.
- **Entangle with deferred default** — `$wire.entangle('open')` gives you an Alpine-friendly two-way proxy that no longer floods the server on every keystroke. Add `.live` when you actually want live.
- **`wire:model` is deferred by default** — same story, different directive. Use `.live`, `.blur`, or `.live.debounce.300ms` depending on what you need.
- **Bundled Alpine — and only one of it** — Magewire ships the CSP build of Alpine inside its JS bundle. If your theme used to load Alpine separately, you can rip that out. One Alpine, one store, no more directive-registration fights.
- **Streaming** — `wire:stream` works. A Magento output-buffering layer made this harder than it should have been, but we got there.
- **Modern morphing, modern commit hooks** — the frontend uses Livewire's current morph algorithm with all its bug fixes. Every request goes through the `commit` hook pipeline, so you can intercept, retry, or observe without hacks.
- **Lifecycle hooks that read like Laravel** — `boot`, `booted`, `mount`, `hydrate`, `updating`/`updated`, `rendering`/`rendered`, `dehydrate`, `exception`. Plus per-property variants (`updatedFirstName`, `hydrateCart`).

None of this is Magewire-specific. It's Livewire V3, running inside Magento, behaving exactly like the Livewire community expects.

## What Magewire adds on top

Some problems are uniquely Magento-shaped, and Magewire takes them seriously.

- **Fragments.** An explicitly-scoped slice of output that Magewire can validate, hash, and decorate before it reaches the browser. That's how CSP support works without you ever touching a nonce. It's also the plumbing behind Flakes and the developer-mode annotations you'll see in DOM devtools.
- **Magewire Flakes.** Drop a `<magewire:dialog name="..." prop:title="$title" mount:foo="bar"/>` tag anywhere in a component template and you get a fully reactive child component, no ViewModel gymnastics, no awkward layout XML for a one-off re-usable piece.
- **Template Directives.** The `@ucfirst('foo')` / `@auth` / `@guest` family you know from Blade, precompiled to real PHP. Extensible too, register your own prefix (`@agencyCustomerGroup(1)`) without patching core.
- **Rate limiting.** Both sides: client-side via `wire:mage:throttle`, and a server-side cache-driven limiter configured from the admin. Use one, use both, use neither. The cache driver is swappable.
- **Observer Events.** Every Magewire lifecycle event is re-emitted as a Magento observer event prefixed `magewire_on_*`. Need to hook `render` from a module? Add an `events.xml` entry, get a typed DTO, ship it. No Component Hook required.
- **A proper notifier.** Fluent API from PHP (`$this->magewireNotifications()->make(...)->asSuccess()`), Alpine-rendered on the frontend, themeable per site. Handles named notifications so you don't stack duplicate toasts.
- **Synthesizers for Magento types.** A DataObject synthesizer ships out of the box. Public properties can hold Magento models without you writing a single line of serialisation glue. Need more? Write your own synthesizer and register it via DI.
- **Area-scoped DI, finally done right.** Features and Mechanisms register in `etc/frontend/di.xml` or `etc/adminhtml/di.xml`. The storefront and admin can ship genuinely different feature sets without the global-DI circus that plagued V1.

## Reaching the admin

Magewire V1 was storefront-only. V3 isn't. A companion package, `magewirephp/magewire-admin`, ships the admin route, the session check, the Prototype.js collision shim, the Renderer plugin that loads Magewire before RequireJS, everything needed to run Magewire components inside Magento's admin panel.

```
composer require magewirephp/magewire-admin
```

Layout XML is the same as storefront. Lifecycle is the same. Alpine is the same (minus Tailwind, the admin has its own styles). Build a reactive grid, an inline editor, a refund wizard, it just works. You still need to add ACL checks in every action, because any public method is a public endpoint. But that part is on you.

## Under the hood

V3 is a complete architectural rewrite. Three concepts you'll see everywhere in the docs:

- **Mechanisms** — the non-removable backbone: component resolving, snapshot handling, request handling, frontend assets. You extend them; you don't delete them.
- **Features** — the optional layer: notifications, rate limiting, streaming, redirects, BC shims. Disabling a feature never breaks the architecture.
- **Component Hooks** — the primitive behind everything. A class that subscribes to lifecycle events (`mount`, `render`, `dehydrate`, …) with middleware semantics. Almost every Feature is one.

Every custom piece you write, a new resolver, a new synthesizer, a new feature, a theme adapter, plugs into this shape. The boundary between core, theme, and userland is clearer than it has ever been.

## Coming from V1

I took backwards compatibility seriously. A V1 component runs on V3 with a single attribute:

```php
use Magewirephp\Magewire\Features\SupportMagewireBackwardsCompatibility\HandleBackwardsCompatibility;

#[HandleBackwardsCompatibility]
class LegacyCart extends \Magewirephp\Magewire\Component { /* ... */ }
```

The BC layer rewrites `wire:model` → `wire:model.live`, re-triggers deprecated event names, proxies `component.data` → `component.$wire`, and a handful of other transforms. You buy time to migrate without rewriting every component on the day you upgrade.

Hyvä Checkout users get even better news: its BC module flips the flag on automatically for every component rendered inside the checkout container, so most existing checkouts run on V3 without touching a single component class.

The full migration checklist lives in the [Upgrade guide](../../pages/getting-started/upgrade.md).

## Give it a spin

That's the tour. Not everything, obviously, the docs cover the rest. But this is the shape of V3, on release day, and I genuinely think it's a better framework than anything I've built before.

```
composer require magewirephp/magewire
```

Try it, break it, open issues, open PRs, send screenshots when you make something cool. Magewire has always been a small, focused project, and it stays alive because people actually use it and actually contribute back.

Thanks for waiting. Now stop reading and go build something reactive.
