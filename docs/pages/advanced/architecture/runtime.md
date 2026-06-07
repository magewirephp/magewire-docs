# Runtime

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

You can build every component you'll ever need without reading this page — Magewire boots
itself automatically. But when you're debugging an edge case, writing a Mechanism or Feature, or
just curious *how* a PHP framework wakes up inside a Magento request, this is the background that
makes the rest of the architecture click.

The **runtime** is a small, request-scoped state machine. Once per request it boots Magewire,
remembers **what kind** of request it is handling, and tracks **where** it is in its own boot
lifecycle. Three pieces of vocabulary cover almost everything:

| Term | Question it answers | Type |
|---|---|---|
| **mode** | What kind of request is this — an initial page load or an update? | `RequestMode` |
| **state** | Where is Magewire in its boot lifecycle right now? | `RuntimeState` |
| **boot mode** | How eagerly should an individual service boot — early, or only when needed? | `ServiceTypeItemBootMode` |

The runtime itself is a single object (`Magewirephp\Magewire\Runtime`) holding just a `mode` and a
`state`, reachable through `MagewireServiceProvider::runtime()`. It lives for one HTTP request and
starts fresh on the next.

## Request modes

The **mode** records which of Magewire's two request shapes is being served:

| Mode | Value | Meaning |
|---|---|---|
| `UNDEFINED` | 0 | No mode set yet — the runtime hasn't been booted. |
| `PRECEDING` | 1 | The **initial full page render**. Components are constructed and mounted as the page's HTML is built. |
| `SUBSEQUENT` | 2 | A **`/magewire/update` XHR**. Components are reconstructed from their snapshot, updated, and re-rendered. |

The mode is **write-once**: the first call to `mode($mode)` sets it, and every later call returns
that value unchanged. It can never be unset back to `UNDEFINED`. This gives the rest of the
framework a single, stable answer to "are we on an update request?":

```php
if ($magewireServiceProvider->runtime()->mode()->isSubsequent()) {
    // e.g. decorate the layout for page-less block loading — see the Layout page.
}
```

`PRECEDING` and `SUBSEQUENT` are the same naming you'll see throughout the architecture: a
*preceding* request renders the page, a *subsequent* request updates a component that was rendered
on a preceding one.

## Runtime state

The **state** tracks Magewire's own boot lifecycle. It only ever moves forward through the happy
path, with two exits:

```
UNINITIALIZED ──▶ SETUP ──▶ BOOTING ──▶ BOOTED
      (0)          (1)        (2)         (3)

                  any step ──▶ FAILED (4)        BOOTED ──▶ STOPPED (5)
```

| State | Value | Meaning |
|---|---|---|
| `UNINITIALIZED` | 0 | Boot process hasn't started. Initial state. |
| `SETUP` | 1 | Containers are booted and the always-on services have run. |
| `BOOTING` | 2 | Actively executing the boot sequence; remaining services are booting. |
| `BOOTED` | 3 | Fully booted and operational. |
| `FAILED` | 4 | A critical error stopped the boot; the request can't proceed. |
| `STOPPED` | 5 | Was running, then gracefully shut down. |

Because the cases are ordered integers, state checks read like comparisons —
`state()->isMinimally(RuntimeState::BOOTED)`, `isAbove(...)`, `isBelow(...)`, `is(...)`,
`isAny([...])`. The boot routine uses this to guard against re-entry: if the state is already at
`BOOTING` or beyond, a second `boot()` call returns immediately instead of booting twice.

## The boot process

Booting happens in two phases — a lightweight **setup** that runs on every controller action, and
a full **boot** that runs only when Magewire is actually needed.

### Phase 1 — `setup()`

Triggered by the `ControllerActionPredispatch` observer on **every** controller action, so the
groundwork is in place before anything renders. It:

1. Fully boots the **Containers** service type.
2. Fires the `magewire:setup` event.
3. Boots the **persistent-and-above** Mechanisms and Features (see [boot modes](#service-types-and-boot-modes)).
4. Moves the state to `SETUP`.

If setup has already run (`state >= SETUP`) it's a no-op, so the cost is paid once per request.

### Phase 2 — `boot(mode)`

Triggered the first time Magewire is genuinely in play. There are exactly **two** trigger points:

- **`ViewBlockAbstractToHtmlBefore`** — when the first block carrying a `magewire` argument is about
  to render on a normal page, it boots with `RequestMode::PRECEDING`.
- **`MagewireUpdateRoute`** — the update endpoint boots with `RequestMode::SUBSEQUENT`.

The boot routine then:

1. Sets the request **mode** (write-once).
2. Runs `setup()` first if the runtime is still `UNINITIALIZED`.
3. Moves the state to `BOOTING`.
4. Fires the `magewire:boot` event, which returns a `finish` callback.
5. Boots the remaining (lazy) Mechanisms and Features that setup skipped.
6. Invokes the `finish` callback — the "after boot" hook, run only when no exception occurred.
7. Moves the state to `BOOTED`.

Any exception along the way flips the state to `FAILED` and re-throws. A `reset(mode)` helper exists
to force a clean re-boot (it sets the state back to `UNINITIALIZED` and boots again), but you should
rarely need it.

## Service types and boot modes

Everything Magewire boots is organised into three **service types**, each a collection of ordered,
individually-bootable items:

| Service type | What it holds |
|---|---|
| **Containers** | Foundational services; always fully booted first, during `setup()`. |
| **Mechanisms** | The required core pipeline steps. See [Mechanisms](mechanisms/index.md). |
| **Features** | Optional, swappable capabilities. See [Features](features.md). |

Each item declares a **boot mode** that controls *when* it boots:

| Boot mode | Value | Boots during |
|---|---|---|
| `LAZY` | 10 | The full `boot()` phase — only when Magewire is actually used. |
| `PERSISTENT` | 20 | `setup()` — early, on every controller action. |
| `ALWAYS` | 30 | `setup()` — early, on every controller action. |

A boot call only runs items whose boot mode is **at or above** the requested level. So `setup()`'s
`boot(PERSISTENT)` starts the `PERSISTENT` and `ALWAYS` items and skips `LAZY` ones; the later full
`boot()` (no minimum) picks up everything that's left. The default boot mode is `ALWAYS`, while
Mechanisms fall back to `LAZY` — most mechanisms only matter once a component is in play.

Within a service type, items boot in `sort_order`, with an optional `sequence` to declare
"boot after this other item" dependencies.

## Hooking into the boot

The boot phases are themselves extension points, dispatched through Magewire's event system. From a
Mechanism, Feature, or [Component Hook](component-hooks.md) you can listen with `on()`:

```php
use function Magewirephp\Magewire\on;

on('magewire:setup', function ($runtime) {
    // Runs once per request, right after containers boot.
});

on('magewire:boot', function ($runtime) {
    // Before the remaining services boot.
    return function () {
        // After a successful boot (the "finish" callback).
    };
});
```

These are the same `on()` / `trigger()` primitives the rest of the lifecycle uses — see
[Component Hooks](component-hooks.md) for the broader hook pipeline.

## Accessing the runtime

Day-to-day component code never touches the runtime. When framework-level code does need it, it
goes through the service provider:

```php
$runtime = $magewireServiceProvider->runtime();

$runtime->mode();   // RequestMode  — preceding / subsequent
$runtime->state();  // RuntimeState — where in the boot lifecycle
```

Treat both as **read-only** from your own code. The framework sets the mode and advances the state
at the right moments; reading them (especially `mode()->isSubsequent()`) is fine and common, but
setting them by hand will desync the boot machinery.

## Related

- [Mechanisms](mechanisms/index.md) — the required core steps booted by the runtime.
- [Features](features.md) — the optional services booted alongside them.
- [Component Hooks](component-hooks.md) — the `on()` / `trigger()` event pipeline used throughout boot.
- [Layout](layout.md) — a concrete consumer of `mode()->isSubsequent()`.