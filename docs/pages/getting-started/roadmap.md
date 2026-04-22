# Roadmap

The roadmap reflects what the core team is actively working on or has committed to. It is not a promise — priorities shift as contributors, sponsors, and real-world usage push the project in new directions. Open issues and PRs are the best source of day-to-day detail; this page zooms out to the season-length view.

## 2025

| Initiative               | Description                                                                                                                                                            | Priority | Status      |
|--------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-------------|
| **Beta Release**         | Finalize V3 beta launch with public code access. Gather community feedback and validate core functionality.                                                            | High     | Finished    |
| **Portman**              | Extract the Livewire → Magewire porting tool into its own reusable package so future Livewire releases can be ported in hours, not weeks.                               | High     | Finished    |
| **Backwards compatibility layer** | Ship the `#[HandleBackwardsCompatibility]` attribute, `memo.bc.enabled` flag, and JS shims so V1 sites upgrade without a full rewrite.                        | High     | Finished    |
| **Admin integration**    | Companion package `magewirephp/magewire-admin` — admin route, session guard, Prototype.js collision shim, head-injection plugin. Bring Magewire to the backend.       | High     | Finished    |
| **Fragments + CSP**      | Typed output fragments with validators and modifiers. Out-of-the-box CSP compliance for inline `<script>` / `<style>`.                                                 | High     | Finished    |
| **Template Directives**  | Blade-style `@directive` syntax inside component templates with a pre-compiler and user-extensible prefixes.                                                            | Medium   | Finished    |
| **Flakes**               | `<magewire:dialog ...>` tag syntax for re-usable inline child components.                                                                                              | Medium   | Finished    |
| **Rate limiting**        | Server-side cache-driven limiter plus client-side `wire:mage:throttle`. Swappable storage adapters.                                                                    | Medium   | Finished    |
| **Observer event bridge** | Mirror every Magewire lifecycle event to Magento's event manager prefixed `magewire_on_*`.                                                                            | Medium   | Finished    |

## 2026

| Initiative                 | Description                                                                                                                                                                            | Priority | Status      |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|-------------|
| **V3 General Availability** | First stable V3 tag. Release blog, migration docs, upgrade guide, changelog automation.                                                                                               | High     | Finished    |
| **Browser Test Suite**     | Grow the Playwright harness beyond the initial `directives.spec.js` fixture. Cover every `wire:*` directive, morph scenario, BC shim, and Feature bridge across both storefront themes. | High     | In Progress |
| **Enhanced Debug Tools**   | A devtools panel that inspects snapshots, memo, effects, queued updates, and commit timeline. Complement the developer-mode fragment attribute already shipped.                        | Medium   | Planning    |
| **Formal validation layer**| Port Livewire's validation rules into Magewire idioms on top of Magento's `Magento\Framework\Validator` where it makes sense.                                                          | Medium   | Not Started |
| **JS evaluation helper**   | `Component::js()` — queue a one-shot JS payload to run on the browser after the next roundtrip. Bring the Livewire V3 helper to Magewire.                                              | Medium   | Planning    |
| **File uploads**           | Port Livewire's file-upload feature. Chunked uploads, progress reporting, temporary storage integration with Magento media filesystems.                                                | Medium   | Not Started |
| **Theme compatibility: Luma** | Ship a Luma-compat module alongside the in-tree Hyvä module so merchants on Luma can adopt Magewire without writing their own theme adapter.                                        | Low      | Not Started |
| **Feature Migration**      | Complete migration of remaining V1-only features and conveniences into V3 idioms under the BC umbrella.                                                                               | Medium   | In Progress |
| **Synthesizers for Magento primitives** | Out-of-the-box synthesizers for `ProductInterface`, `OrderInterface`, `CustomerInterface`, `CartInterface`, and `AddressInterface` so components can hold them directly. | Medium   | Planning    |
| **Performance profiling**  | Built-in profiling fragment modifier that annotates the DOM with per-component timings in developer mode. Surface hotspots without leaving the page.                                   | Low      | Planning    |
| **Documentation polish**   | Close the gap with Livewire's docs — more worked examples, more screenshots, clearer "choose this over that" decision tables.                                                          | High     | In Progress |

## Beyond 2026

Ideas that are on the table but not scheduled. Ordering here is arbitrary.

- **First-class SSE / long-lived sockets** — a streaming story that outgrows `wire:stream` and doesn't depend on PHP-FPM output buffering.
- **Form Objects** — Livewire V3's form-object pattern ported and wired to Magento's EAV / customer / quote models.
- **Server-side navigation** — a `wire:navigate` implementation that plays nicely with Magento's layout cache and FPC.
- **Breeze / Magento Open Source legacy** theme adapters — community-driven, not a core commitment, but the theming architecture supports it.
- **Codegen and scaffolding CLI** — `bin/magento magewire:make:component …` to generate a component, template, and layout registration in one shot.

## How to influence the roadmap

This is an open source project with a handful of regular contributors, so the two levers that actually move items up the list are:

- **Contribute code.** A PR with tests and docs is the fastest route from "planned" to "shipped". Even partial work on a ticket is valuable — it makes the rest tractable.
- **Sponsor.** Sponsorship funds time that would otherwise go to paid work. It is the only reason Magewire V3 exists in the shape it does — thanks Vendic and Hyvä.

If you want to see an item moved up, argue for it on the issue tracker with a concrete use case. "We'd use this on X site for Y reason" beats "would be nice to have" every time.

## Status legend

| Status | Meaning |
|---|---|
| **Finished** | Shipped on a tagged release. |
| **In Progress** | Actively being built. PRs land under this label. |
| **Planning** | Design phase — scope, API, and integration points being decided. |
| **Not Started** | On the list; no active work yet. |
