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

```xml title="File: etc/frontend/di.xml"
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

### Module structure

We encourage everyone to use the `src/` root folder within your module for all Magewire-related code.
Components should reside directly in this folder or be organized into subdirectories.
Features should also be placed within `src/`, using a `Features/` folder.

Each feature should be grouped inside a `Support`-prefixed subfolder, which contains everything related to that feature.

As a general rule within the core, feature naming follows a prefix convention:

- If it's a Magewire-specific feature, prefix it with `SupportMagewire`.
- If it's intended to make a Magento feature compatible with Magewire, use the `SupportMagento` prefix.

This isn't a strict requirement, but it’s considered a best practice for consistency.

### JavaScript
You can extend your feature to the frontend by adding JavaScript functionality when required.

This JavaScript code doesn't live within the feature folder itself, but must be organized within the `/view` subfolder structure.
For complete details on implementing JavaScript features, refer to the [Features JavaScript](../javascript/index.md#features) paragraph.

### Hooks

The Livewire (and by extension, Magewire) architecture was designed with extensibility in mind, allowing developers to hook into certain processes before or after they occur.

A general rule applies:

- Hooks must always return either a callback (which serves as the method to be executed after the process completes) or the original result from the hook.
- When using a callback, the result is automatically injected as an argument, allowing you to modify it if needed. However, you must always return the same result from the callback to maintain consistency.

#### FAQ

| Question                                     | Answer                                                                                                                                                                                                                                                                                                                 |
|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| When do I use hooks?                         | Only hook into specific Magewire processes or trigger your own events in areas of your code where you need to listen for them elsewhere.                                                                                                                                                                               |
| Are these hooks the same as Observer Events? | No, the goal is to eventually provide developers with the ability to listen for events using standard observer events. While this is still an idea, we hope to implement it in the future to align more closely with Magento's principles. In the meantime, we recommend following the approach suggested by Livewire. |

#### Example

```php title="Magewire/Features/SupportExample"
<?php

use function Magewirephp\Magewire\on;

class SupportExample extends \Magewirephp\Magewire\ComponentHook
{
    on('magewire:construct', function () {
        // Before
        
        return function (AbstractBlock $block) {
        
            // After
            return $block;
        };
    });
}
```

The above example is triggered in the core using `$construct = trigger('magewire:construct', $block)`, where the result
is assigned to a variable. The event listener receives the $block, but instead of directly returning it,
it returns a callback that also accepts the `$block` argument. This callback is then triggered later in the code with `$construct()`.


