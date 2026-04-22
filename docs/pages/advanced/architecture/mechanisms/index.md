# Mechanisms

{{ include('admonition/livewire-concept.md') }}

Magewire is composed of three layers: the Magento module that loads everything, **Mechanisms** (required core steps), and **Features** (optional extensions). This page covers Mechanisms.

## Mechanism vs. Feature

| | Mechanism | Feature |
|---|---|---|
| Optional | No | Yes |
| Can be disabled | No | Yes — or replaced via DI |
| Runs per request | Every request | Only when registered |
| Examples | ResolveComponents, HandleRequests | SupportMagewireNotifications, SupportMagewireRateLimiting |

Mechanisms form the non-negotiable core pipeline. Removing any of them breaks the framework.

## The pipeline

Every Magewire request passes through the mechanisms in sort-order sequence:

```
ResolveComponents (1000)
   ↓
PersistentMiddleware (1050)
   ↓
HandleComponents (1100)
   ↓
HandleRequests (1200)
   ↓
DataStore (1250)
   ↓
FrontendAssets (1400)
```

## Built-in mechanisms

| Name | Sort order | Responsibility |
|---|---|---|
| **ResolveComponents** | 1000 | Discover components attached to Magento blocks. Runs component resolvers until one matches; binds the resolved component to the block. |
| **PersistentMiddleware** | 1050 | Keeps state needed across the page render (layout handles, resolver metadata) available for later mechanisms. |
| **HandleComponents** | 1100 | Runs the lifecycle pipeline for each component — boot, mount/hydrate, updates, render, dehydrate. Applies synthesizers for each public property. |
| **HandleRequests** | 1200 | On AJAX updates: receives the POST to `/magewire/update`, validates the snapshot checksum, invokes HandleComponents, assembles the response. |
| **DataStore** | 1250 | Per-component request-scoped key/value store used by features (BC flag, rate-limit counters, feature-owned state). Accessed via `store($component)->get/set(…)`. |
| **FrontendAssets** | 1400 | Emits the JS/CSS assets — the Magewire bundle, inline setup scripts, CSP fragments, nonces. |

## Registering / overriding

Mechanisms are declared on `Magewirephp\Magewire\Mechanisms` via DI. The two supported shapes:

```xml title="etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Mechanisms">
    <arguments>
        <argument name="items" xsi:type="array">

            <!-- Long form — with optional metadata -->
            <item name="resolve_components" xsi:type="array">
                <item name="type" xsi:type="string">
                    Magewirephp\Magewire\Mechanisms\ResolveComponents\ResolveComponents
                </item>
                <item name="sort_order" xsi:type="number">1000</item>
                <item name="view_model" xsi:type="object">
                    Magewirephp\Magewire\Mechanisms\ResolveComponents\ResolveComponentsViewModel
                </item>
            </item>

            <!-- Short form -->
            <item name="frontend_assets" xsi:type="string" sortOrder="1400">
                Magewirephp\Magewire\Mechanisms\FrontendAssets\FrontendAssets
            </item>
        </argument>
    </arguments>
</type>
```

To override a mechanism in a specific area, declare the replacement class in `etc/frontend/di.xml` or `etc/adminhtml/di.xml` with the same item name. Replacing is what `magewire-admin` does to patch the admin-specific update route and component resolver — see [Admin → How it works](../../../admin/how-it-works.md).

## Adding a custom mechanism

Rare. Only reach for a custom mechanism when a behaviour must run on **every** request and cannot be expressed as a [Component Hook](../component-hooks.md). In practice: custom authentication on the update controller, custom asset pipelines, or replacing the snapshot transport entirely.

For everything else, a Feature backed by a Component Hook is lighter and safer.

## Laravel leftovers

Livewire ships a handful of Laravel-specific mechanisms (routing macros, session bridging). They live in the source tree so Magewire can keep Livewire upstream in sync via [Portman](../portman.md), but they are unregistered in Magewire's container and do nothing at runtime.

## Related

- [Component Hooks](../component-hooks.md)
- [Features](../features.md)
- [Resolvers](resolvers.md) — the ResolveComponents mechanism in depth.
- [Layout](../layout.md) — how FrontendAssets surfaces layout containers.
