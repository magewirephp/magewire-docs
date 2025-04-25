# Mechanisms

{{ include('admonition/livewire-concept.md') }}

Magewire is divided into three aspects. First, there is the architecture itself, which includes the module responsible
for loading everything within Magento, as well as specific Livewire concepts. Those other two aspects within this architecture
are **Features** and **Mechanisms**.

In this documentation, we will focus specifically on **Mechanisms**.

## Concept

The idea behind Mechanisms is that they are essential components required for Magewire to function.
They form a foundational part of the architecture and cannot be removed or treated as optional.

As such, Mechanisms are typically core elements of Magewire, rather than being designed for injection or replacement
through third-party extensions.

## Example

We use **Resolvers** as an example.

Magewire Resolvers are critical components responsible for binding Magewire objects to blocks,
effectively transforming them into Magewire components.

Removing Resolvers would constitute a breaking change, as blocks intended to function as Magewire components would
no longer be able to do so.

```xml title="File: etc/frontend/di.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:ObjectManager/etc/config.xsd"
>
    <type name="Magewirephp\Magewire\Mechanisms">
        <arguments>
            <!-- Option #1. -->
            <argument name="items" xsi:type="array">
                <item name="resolve_components" xsi:type="array">
                    <item name="type" xsi:type="string">
                        Magewirephp\Magewire\Mechanisms\ResolveComponents\ResolveComponents
                    </item>
                    
                    <!-- Optional. -->
                    <item name="sort_order" xsi:type="number">
                        1000
                    </item>
                    <item name="view_model" xsi:type="object">
                        Magewirephp\Magewire\Mechanisms\ResolveComponents\ResolveComponentsViewModel
                    </item>
                </item>
            </argument>
            
            <!-- Option #2. -->
            <item name="resolve_components" xsi:type="string" sortOrder="1000">
                Magewirephp\Magewire\Mechanisms\ResolveComponents\ResolveComponents
            </item>
        </arguments>
    </type>
</config>
```

## Mechanisms

The following mechanisms form the backbone of Magewire and are essential to its operation.

| Name                    | Description | Sort Order |
|-------------------------|-------------|------------|
| **Frontend Assets**     | WIP         | 1400       |
| **Handle Components**   | WIP         | 1100       |
| **Handle Requests**     | WIP         | 1200       |
| **Resolver Components** | WIP         | 1000       |
| **Persist Middleware**  | WIP         | 1050       |
| **Data Store**          | WIP         | 1250       |

!!! info "While Livewire contains various Laravel-specific mechanisms, these are present in the source code but remain unused in the context of Magewire."
