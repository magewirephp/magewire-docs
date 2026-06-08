# HandleRequests

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

`HandleRequests` (sort order `1200`) is the entry point for **subsequent** requests — the
`/magewire/update` XHR that fires when a user interacts with a component. It receives the POST,
drives [HandleComponents](handle-components.md) for each component in the payload, and assembles the
JSON response.

On an initial page render this mechanism does nothing; the work happens only on update roundtrips.

## The update flow

A Magewire update is a single POST carrying one or more component payloads. `handleUpdate()` walks
them:

1. Read the `components` array from the request.
2. Fire the `request` event (lets features inspect/transform the raw payload).
3. For **each** component payload:
   - `magewire:component:reconstruct` — rebuild the block and component from the snapshot
     (via its [resolver](resolvers.md)).
   - Mark the component as updating: `store($component)->set('magewire:update', $payload)`.
   - Render the block (`$block->toHtml()`), which runs the component lifecycle through
     [HandleComponents](handle-components.md).
   - Collect the new `snapshot` and `effects`.
4. Fire the `response` event and return the assembled payload:

```json
{
  "components": [
    { "snapshot": "…serialized snapshot…", "effects": { "…": "…" } }
  ],
  "assets": []
}
```

The browser runtime takes each component's new snapshot and effects, morphs the DOM, and applies the
effects (redirects, dispatched events, flash messages, …).

## Identifying a Magewire request

```php
$handleRequests->isMagewireRequest(); // true on a /magewire/update XHR
```

Internally this just asks the [runtime](../runtime.md) whether the mode is `SUBSEQUENT` — the single
source of truth for "are we on an update request?".

!!! info "Routing is Magento's, not Livewire's"
    The ported Livewire class still carries Laravel route helpers (`findUpdateRoute()`, route
    macros). In Magewire those are **Portman leftovers** — the actual endpoint is wired through a
    Magento controller (`MagewireUpdateRoute`), which boots the runtime in `SUBSEQUENT` mode and
    hands off to this mechanism. The update URI is exposed to templates via
    `utils()->magewire()->getUpdateUri()` (see [View Model & Utilities](../../../essentials/view-model.md)).

## Related

- [Mechanisms](index.md) — the pipeline overview.
- [HandleComponents](handle-components.md) — the lifecycle this mechanism invokes per component.
- [Runtime](../runtime.md) — `SUBSEQUENT` mode and the boot trigger.
- [Resolvers](resolvers.md) — how each component is reconstructed from its snapshot.