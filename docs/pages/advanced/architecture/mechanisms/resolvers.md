# Resolvers

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Component Resolvers are responsible for constructing a valid block having a Magewire argument—essentially,
a data `object` element that represents a Magewire Component.

By default, thanks to Layout XML, blocks are automatically generated, and when a Magewire argument is added,
the block is dynamically transformed. While this appears seamless, behind the scenes, the **Layout Component Resolver**
is actually handling the process.

However, in many other cases—such as with [Magento Widgets](https://experienceleague.adobe.com/en/docs/commerce-admin/content-design/elements/widgets/widgets)—the standard layout approach doesn’t apply. In these scenarios, the block must receive its Magewire argument differently
and mount the component in an alternative way.

The Resolver mechanism (or API) provides the flexibility to handle these cases.

## Responsibilities

In all default Layout XML scenarios, no resolver needs to be added unless a specific case requires behavior different from the standard layout resolver. For most other scenarios, the package will either provide a suitable resolver out of the box, or a custom one will need to be written.

At its core, a component resolver is responsible for the following:

1. Verifying block compliance – Determines whether a block meets the required conditions to be used as a component resolver (method: `complies`).
2. Constructing the component on page load (method: `construct`). 
3. Reconstructing the component during a subsequent (XHR) request (method: `reconstruct`). 
4. Providing the lifecycle with an arguments object (method: `arguments`).

Additional methods exist within the abstraction but are optional, depending on the use case.

## Lifecycle

Behind the scenes, Magewire checks **every** block that attempts to render itself to see if it contains a `magewire` data element.
If it does, regardless of its value, the Magewire lifecycle will automatically attempt to construct it.

At this point, the block is passed through the `complies` method to determine whether it belongs to your custom resolver.

If all conditions are met, that resolver will be used to construct the block and reconstruct it when a subsequent request
is triggered on the frontend.

Thanks to the `remember` method returning `true`, a cache if being applied, preventing the need to repeatedly check
whether it meets the resolver’s requirements.

## Example

!!! warning "creating a custom resolver is intended for more advanced Magewire developers who have a solid understanding of the Magewire lifecycle and how to connect various pieces of data effectively."

A resolver is essentially a single class that extends the resolver abstraction and implements a few required methods to
determine whether it applies to a given block.

Because Magento works primarily with blocks, it will be most likely your custom resolver will extend from the `layout` resolver.

```php
<?php

declare(strict_types=1);

namespace Example\Module\Mechanisms\ResolveComponents\ComponentResolver;

use \Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentResolver\ComponentResolver\LayoutResolver

class ExampleResolver extends LayoutResolver
{
    protected string $accessor = 'example';

    // A lightweight check to determine if the given block meets the requirements 
    // to be resolved using this resolver.
    public function complies(AbstractBlock $block, mixed $magewire = null): bool
    {
        return $block->hasData('foo') && $block->getData('foo') === 'bar';
    }
    
    // Constructs a block, initializes a Magewire component object, and sets its ID and name.
    public function construct(AbstractBlock $block): AbstractBlock
    {
        $block->setData('magewire') = $myCustomComponentFactory->create($block)
    
        return parent::construct($block);
    }

    // Reconstructing the block from the given snapshot during an update request cycle.
    public function reconstruct(\Magewirephp\Magewire\Mechanisms\HandleRequests\ComponentRequestContext $request): AbstractBlock
    {
        $snapshot = $request->getSnapshot();

        return parent::reconstruct($request);
    }
}
```

Finally, make the resolver accessible through the **Component Resolver Management** by configuring it in `di.xml`.

```xml title="File: etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentResolverManagement">
    <arguments>
        <argument name="resolvers" xsi:type="array">
            
            <!-- The sort order defines which resolver is evaluated first and should always be set. -->
            <item name="layout" xsi:type="object" sortOrder="1337">
                Magewirephp\Magewire\Mechanisms\ResolveComponents\ComponentResolver\LayoutResolver
            </item>
        </argument>
    </arguments>
</type>
```
