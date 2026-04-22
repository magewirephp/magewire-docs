# Resolvers

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

A **Component Resolver** is the bridge between a Magento `AbstractBlock` and a Magewire `Component`. Given a block, the resolver decides whether it should become a component, builds the component on the initial page render, and rebuilds it on every subsequent `/magewire/update` XHR.

For the default Layout-XML flow (a block with a `<argument name="magewire" xsi:type="object">…</argument>`), the built-in `LayoutResolver` handles everything. You only need a custom resolver when the component's binding shape isn't a plain layout argument — Magento Widgets, dynamically-generated blocks, data-driven component construction, or anything that doesn't fit the standard layout model.

## Mental model

Think of a resolver as a three-state machine with a stable identity:

```
(block arrives)  →  complies?  →  construct()  →  snapshot (accessor stored in memo)
                                                     │
                              XHR update             ▼
                (block gone)  ←  reconstruct(request)
```

- **`complies()`** — a cheap yes/no question the manager asks every registered resolver until one says yes.
- **`construct()`** — runs once per initial render. Hands back the block with a `Component` bound to it.
- **`reconstruct()`** — runs on every update roundtrip. Must rebuild the block/component from *only* the incoming snapshot (no layout state survives the HTTP hop).
- **`getAccessor()`** — a unique short name (`layout`, `flake`, `layout_admin`). Stored in the snapshot memo so the same resolver is picked on reconstruction. Must match the DI item name.

## Responsibilities

A resolver must implement four abstract methods and may override `remember()`:

| Method | Purpose |
|---|---|
| `complies(AbstractBlock $block, mixed $magewire = null): bool` | Cheap check. Returns `true` if this resolver should handle the block. |
| `construct(AbstractBlock $block): AbstractBlock` | Attach a `Component` to the block (via `$block->setData('magewire', $component)`) and return the block. |
| `reconstruct(ComponentRequestContext $request): AbstractBlock` | Rebuild the block + component from the XHR snapshot. |
| `arguments(): MagewireArguments` | Provide the typed arguments object that collects `magewire.*` / `magewire:*` data keys from the block. |
| `remember(): bool` *(optional)* | Cache the resolver/block pairing. Defaults to `true`. Return `false` for a fluent resolver that re-evaluates conditions per request. |

## How the manager picks a resolver

`ComponentResolverManager::resolve($block)` runs in this order:

1. **Snapshot cache.** If the block was resolved before, the previous accessor is pulled from cache — skips `complies()` entirely.
2. **Manual selection.** `$block->setData('magewire:resolver', 'accessor')` forces a specific resolver by name or class string — useful for testing or edge cases.
3. **`complies()` scan.** Every registered resolver is tested in registration order; the first `true` wins.
4. **Not found.** Throws `ComponentResolverNotFoundException`.

Sort order in DI determines step 3's evaluation order. Lower sort orders run first — which is why `FlakeResolver` (98900) is tested before `LayoutResolver` (99900) in core: the more specific resolver gets first refusal.

## The built-in `LayoutResolver`

Worth reading before writing your own — every custom resolver for block-based components should extend it.

```php
// Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentResolver\LayoutResolver

public function construct(AbstractBlock $block): AbstractBlock
{
    $magewire = $block->getData('magewire') ?? null;

    if (! $magewire) {
        throw new ComponentNotFoundException(sprintf('No component object found for "%s"', $block->getNameInLayout()));
    }

    // Supports both <argument name="magewire" xsi:type="object">...</argument>
    // and <argument name="magewire" xsi:type="array"><item name="type" xsi:type="object">...</item></argument>
    $component = is_array($magewire) ? $magewire['type'] : $magewire;

    $block->setData('magewire', $component);

    // On dehydrate, stash the active layout handles into the snapshot memo
    // so reconstruct() can rebuild the layout on the next XHR.
    on('dehydrate', function (Component $component, ComponentContext $context) {
        if ($component->magewireResolver()->getAccessor() === $this->getAccessor()) {
            $context->addMemo('handles', $this->determineLayoutHandles($component, $context));
        }
    });

    return $block;
}

public function reconstruct(ComponentRequestContext $request): AbstractBlock
{
    $snapshot = $request->getSnapshot();
    $handles  = $snapshot->getMemoValue('handles') ?? [];

    // Replay layout with the stored handles, fetch the block by name, reuse construct().
    $block = $this->generateBlocks($handles)[$snapshot->getMemoValue('name')];

    return $this->construct($block);
}
```

The key insight: **reconstruction replays the layout handles**, then re-enters the same `construct()` path. This is why layout XML is the whole source of truth — snapshots only carry enough memo to replay the layout.

## Writing a custom resolver

!!! warning "Creating a custom resolver is intended for advanced Magewire developers who have a solid understanding of the Magewire lifecycle and how the snapshot / memo flow connects the pieces."

Extend `LayoutResolver` when your component is still block-based but needs a different matching rule or extra construction logic. Extend the abstract `ComponentResolver` only when the block-and-argument model genuinely doesn't fit.

### Example 1: Convention-based resolver

A resolver that auto-wires a component onto any block whose class name ends in `ReactiveBlock` — useful for module authors who want to drop a marker interface instead of writing layout arguments:

```php
<?php

declare(strict_types=1);

namespace Vendor\Module\Mechanisms\ResolveComponents\ComponentResolver;

use Magento\Framework\View\Element\AbstractBlock;
use Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentResolver\LayoutResolver;
use Vendor\Module\Component\ReactiveBlockComponentFactory;

class ReactiveBlockResolver extends LayoutResolver
{
    protected string $accessor = 'reactive_block';

    public function __construct(
        private readonly ReactiveBlockComponentFactory $factory,
        // …pass through parent deps
    ) {
        // parent::__construct(...);
    }

    public function complies(mixed $block, mixed $magewire = null): bool
    {
        if (! $block instanceof AbstractBlock) {
            return false;
        }

        return str_ends_with($block::class, 'ReactiveBlock');
    }

    public function construct(AbstractBlock $block): AbstractBlock
    {
        // No magewire argument in layout XML — synthesize one from the block class.
        if (! $block->hasData('magewire')) {
            $block->setData('magewire', $this->factory->createFor($block));
        }

        return parent::construct($block);
    }
}
```

Register with a sort order **lower** than `layout` (99900) so `complies()` runs first:

```xml title="etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Mechanisms\ResolveComponents\Management\ComponentResolverManager">
    <arguments>
        <argument name="resolvers" xsi:type="array">
            <item name="reactive_block" xsi:type="object" sortOrder="90000">
                Vendor\Module\Mechanisms\ResolveComponents\ComponentResolver\ReactiveBlockResolver
            </item>
        </argument>
    </arguments>
</type>
```

!!! info "DI item name matches the accessor"
    The `name="reactive_block"` attribute in DI *must* match `$accessor` on the resolver class. The manager uses this mapping during reconstruction to instantiate the correct class from the snapshot memo.

### Example 2: Layout-handle-scoped resolver (FlakeResolver pattern)

The real `FlakeResolver` claims any block on a page that activates the `magewire_flakes` handle, auto-wiring a lightweight component when no Magewire object is bound:

```php
class FlakeResolver extends LayoutResolver
{
    public const FLAKES_HANDLE = 'magewire_flakes';

    protected string $accessor = 'flake';

    public function complies(mixed $block, mixed $magewire = null): bool
    {
        $this->conditions()->if(static fn () => $block instanceof AbstractBlock);
        $this->conditions()->if(static fn () =>
            in_array(self::FLAKES_HANDLE, $block->getLayout()->getUpdate()->getHandles())
        );

        return $this->conditions()->evaluate($block, $magewire);
    }

    public function construct(AbstractBlock $block): AbstractBlock
    {
        // If the block has an alias but no component, synthesize one so it still "has powers".
        if ($block->hasData('magewire:alias') && ! $block->hasData('magewire')) {
            $block->setData('magewire', $this->flakeFactory->create());
        }

        return parent::construct($block);
    }

    protected function canMemorizeLayoutHandles(): bool
    {
        return false; // Flakes manage their own handles.
    }

    protected function recoverLayoutHandles(Snapshot $snapshot): array
    {
        return [self::FLAKES_HANDLE];
    }
}
```

Two takeaways worth copying:

- **`$this->conditions()`** — a readable builder for `complies()` rules. Each `->if()` adds an AND; `->or()` adds alternates. `evaluate()` returns the final boolean.
- **Override `canMemorizeLayoutHandles()` / `recoverLayoutHandles()`** — swap the snapshot's default "store active handles" strategy when the layout is scripted rather than serialised.

### Example 3: Widget resolver (non-layout binding)

Magento Widgets instantiate blocks through the widget system, not layout XML — so there is no opportunity to add a `magewire` argument. A widget resolver can construct a Magewire component from the widget's parameters instead:

```php
class WidgetResolver extends LayoutResolver
{
    protected string $accessor = 'widget';

    public function complies(mixed $block, mixed $magewire = null): bool
    {
        if (! $block instanceof AbstractBlock) {
            return false;
        }

        // Widgets carry their template path through the 'template' data key
        // and typically live under a known namespace.
        return $block->hasData('widget_type')
            && str_starts_with((string) $block->getData('widget_type'), 'Vendor\\Module\\Widget\\');
    }

    public function construct(AbstractBlock $block): AbstractBlock
    {
        $widgetType = $block->getData('widget_type');
        $parameters = $block->getData() ?? [];

        $component = $this->widgetComponentFactory->createFor($widgetType, $parameters);

        $block->setData('magewire', $component);

        return parent::construct($block);
    }
}
```

The component's `mount()` receives the widget parameters (pass them through your factory); state then survives the XHR like any other component.

## Forcing a resolver manually

When the automatic `complies()` scan is too broad or too narrow, bind a resolver explicitly via the `magewire:resolver` data key. The value is either a registered accessor name or a fully-qualified class string:

```xml
<block name="product.custom"
       template="Vendor_Module::magewire/custom.phtml">
    <arguments>
        <argument name="magewire:resolver" xsi:type="string">reactive_block</argument>
        <argument name="magewire" xsi:type="object">Vendor\Module\Magewire\Custom</argument>
    </arguments>
</block>
```

Works in both layout XML and programmatic block construction. The manager skips `complies()` entirely when this key is present.

## The `remember()` cache

`ComponentResolverManager` caches `{block cache key → resolver accessor}` pairs after a successful resolution — the next page load (or XHR) skips `complies()` for that block. This is controlled per resolver by `remember()`:

```php
public function remember(): bool
{
    return true; // default — cache the pairing
}
```

Return `false` when the resolver's match conditions depend on runtime state (customer group, session flags, A/B experiment assignment, etc.) that a cached pairing would stale through.

Cost of `remember() === false`: every page render pays the full `complies()` scan. Only switch off when the dynamic behaviour is worth it.

## Registration summary

```xml title="etc/frontend/di.xml (and adminhtml/di.xml if needed)"
<type name="Magewirephp\Magewire\Mechanisms\ResolveComponents\Management\ComponentResolverManager">
    <arguments>
        <argument name="resolvers" xsi:type="array">
            <!-- Sort order is required; lower runs first. -->
            <!-- 98900 — flake     (more specific)   -->
            <!-- 99900 — layout    (default fallback) -->
            <item name="my_custom" xsi:type="object" sortOrder="95000">
                Vendor\Module\Mechanisms\ResolveComponents\ComponentResolver\MyCustomResolver
            </item>
        </argument>
    </arguments>
</type>
```

Rules of thumb:

- **Accessor name** matches the DI `name` attribute exactly.
- **Sort order** — put more-specific resolvers below 99900 so they are evaluated before the default layout resolver.
- **Area scope** — register in `etc/frontend/di.xml` for storefront, `etc/adminhtml/di.xml` for admin. The admin package's `LayoutAdminResolver` is the canonical adminhtml example.
- **Never register in global `etc/di.xml`** — Magewire's service provider only reads area-scoped DI.

## When to reach for a custom resolver

Good fit:

- Components bound through a mechanism other than layout XML (widgets, CMS blocks, dynamically generated blocks).
- Convention-based wiring (e.g. any block in a namespace, any block with a marker interface).
- Components whose construction needs runtime data that can't be expressed as a layout argument.

Overkill:

- A component that differs from a standard one only by the data you pass to `mount()` — just use `magewire:mount:*` arguments with the default `LayoutResolver`.
- A component that needs different *behaviour* per page — that's what `boot()` / lifecycle hooks are for.
- Per-theme tweaks — use layout overrides, not a new resolver.

## Related

- [Mechanisms](index.md) — the broader pipeline resolvers plug into.
- [Component Hooks](../component-hooks.md) — extend lifecycle without a new resolver.
- [Admin → How it works](../../../admin/how-it-works.md) — `LayoutAdminResolver` walkthrough.
- [Magewire Flakes](../../../features/magewire-flakes.md) — real-world secondary resolver in core.
