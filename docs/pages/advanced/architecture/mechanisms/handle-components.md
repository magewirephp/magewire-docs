# HandleComponents

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

`HandleComponents` (sort order `1100`) is the heart of the pipeline. It runs a component's lifecycle
and owns the **snapshot** — the serialisable representation of a component's state that travels
between the server and the browser.

Where [ResolveComponents](resolvers.md) decides *which* component a block becomes, `HandleComponents`
decides *what happens* to it: boot, mount or hydrate, apply updates, render, dehydrate.

## What it does

| Operation | Method | When |
|---|---|---|
| **Mount** | `mount($name, $params, $key, $block, $component)` | Initial render — build a fresh component and run `mount()`. |
| **Update** | `update($snapshot, $updates, $calls, $block)` | An XHR update — restore from snapshot, apply property updates and method calls, re-render. |
| **From snapshot** | `fromSnapshot($snapshot, $block)` | Rebuild a component instance from an incoming snapshot. |
| **Snapshot** | `snapshot($component, $context)` | Dehydrate a component into a `Snapshot`. |
| **Update a property** | `updateProperty($component, $path, $value, $context)` | Apply a single incoming property change (public properties only). |

Each operation runs the lifecycle events other parts of the framework hook into — `mount`,
`hydrate`, `update`, `call`, `render`, `dehydrate` (see [Component Hooks](../component-hooks.md) and
[Lifecycle Hooks](../../../essentials/lifecycle-hooks.md)).

## The snapshot

A `Snapshot` is three things:

| Part | Holds |
|---|---|
| `data` | The component's public property values (dehydrated through synthesizers). |
| `memo` | Metadata needed to reconstruct the component — name, id, resolver accessor, layout handles, feature flags. |
| `checksum` | An integrity hash over `data` + `memo`. |

On every update the incoming snapshot's checksum is **verified** before anything else runs — if it
doesn't match, the payload was tampered with and the request is rejected
(`CorruptComponentPayloadException`). This is why public properties are safe to round-trip but must
not be trusted blindly: see [Locked properties / security](../../security.md).

## Synthesizers

Property values aren't always plain scalars. **Synthesizers** teach `HandleComponents` how to
dehydrate and hydrate richer types — arrays, `\stdClass`, backed enums, and Magento's
`\Magento\Framework\DataObject`. Each public property is matched to a synth during snapshot and
restore.

Register your own by adding it to the `synthesizers` argument of the mechanism in DI:

```xml title="etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Mechanisms\HandleComponents\HandleComponents">
    <arguments>
        <argument name="synthesizers" xsi:type="array">
            <item name="my_type" xsi:type="string">
                Vendor\Module\Magewire\Synthesizers\MyTypeSynth
            </item>
        </argument>
    </arguments>
</type>
```

See [Synthesizers](../../synthesizers.md) for writing one.

## Related

- [Mechanisms](index.md) — the pipeline overview.
- [Resolvers](resolvers.md) — what runs before this mechanism.
- [HandleRequests](handle-requests.md) — what drives this mechanism on an XHR.
- [Synthesizers](../../synthesizers.md) — custom property (de)hydration.
- [Hydration](../../../concepts/hydration.md) — the snapshot round-trip concept.
