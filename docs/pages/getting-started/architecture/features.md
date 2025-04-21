# Features

{{ include('admonition/livewire-concept.md') }}

Magewire is divided into three aspects. First, there is the architecture itself, which includes the module responsible
for loading everything within Magento, as well as specific Livewire concepts. Those other two aspects within this architecture
are **Features** and **Mechanisms**.

In this documentation, we will focus specifically on **Features**.

## Concept

The idea behind Features is that they are primarily optional and can be disabled without affecting the core principles of Magewire.
In that sense, they are considered nice-to-haves.

Any third-party additions to Magewire will mainly come in the form of Features and can be integrated separately through other modules.

## Example

We use **Directives** as an example.

Magewire Directives allow you to add directives prefixed with `@` within Magewire-driven block templates.
These directives use bound parsers to transform them into a specific output.

For instance, consider `@ucfirst('foo')`, which would render as `Foo`.

Now, you might wonder: *If I disable this feature, won't `@ucfirst` just appear as plain text in my template?*
That’s correct—but it won’t break the architecture, and everything else will continue to function as expected.

So, while in this particular example, you would likely never want to disable or remove **Directives**, the possibility still exists.

## Write your own

To create and activate your own custom feature, you must inject it into the Features service type. This ensures it is properly executed within the system.

```xml title="File: frontend/di.xml"
<?xml version="1.0"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="urn:magento:framework:ObjectManager/etc/config.xsd"
>
    <type name="Magewirephp\Magewire\Features">
        <arguments>
            <!-- Option #1. -->
            <argument name="items" xsi:type="array">
                <item name="magewire_compiling" xsi:type="array">
                    <item name="type" xsi:type="string">
                        Magewirephp\Magewire\Features\SupportMagewireCompiling\SupportMagewireCompiling
                    </item>
                    <item name="sort_order" xsi:type="number">
                        99100
                    </item>
                </item>
            </argument>
            
            <!-- Option #2. -->
            <item name="magewire_compiling" xsi:type="string" sortOrder="99100">
                Magewirephp\Magewire\Features\SupportMagewireCompiling\SupportMagewireCompiling
            </item>
        </arguments>
    </type>
</config>
```
