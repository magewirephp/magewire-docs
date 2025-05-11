# Basics

Just getting started with Magewire and want to learn the basics? This page will help you kickstart your development journey!

## Layout XML

The primary method for converting a block into a dynamic Magewire component is by defining the `magewire` block argument
and assigning it a component object using the `layout` resolver.

!!! tip "Refer to the [Resolvers](../advanced/architecture/mechanisms/resolvers.md) section for a deeper understanding of how components are bound to blocks."

### Arguments

Since Magewire V3, you can pass arguments to components via block data using the magewire prefix,
followed by either a dot `.` or a colon `:` separator.

- Use `magewire.` for individual component property values.
- Use `magewire:` for grouped arguments.

```xml
<block name="counter" template="Example_Module::magewire/counter.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object">
            ...
        </argument>
        
        <!-- Single public $foo property value assignment. -->
        <argument name="magewire.foo" xsi:type="string">
            baz
        </argument>
        
        <!-- Grouped for specific purposes like the "mount" or "boot" method. -->
        <argument name="magewire:mount:start" xsi:type="number">
            19
        </argument>
    </arguments>
</block>
```

!!! warning "Adding arguments to the `mount` method via layout XML should not be mistaken for standard dependency injection used in the `__construct` method."

The component looks like:

```php
<?php

class Counter extends \Magewirephp\Magewire\Component
{
    // Value of $foo becomes "baz" thanks to the "magewire.foo" XML argument.
    public string $foo = 'bar';
    
    public int $count = 0;
    
    public function mount(int $start = 1337)
    {
        // Value of $count becomes "19" thanks to the "magewire:mount:start" XML arguments.
        $this->count = $start;
    }
}
```

### Object Reusability

Magento natively supports object reusability through the `shared="false"` argument attribute,
which allows you to control whether a new instance is created each time.

```xml
<block name="counter" template="Example_Module::magewire/counter.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object" shared="false">
            ...
        </argument>
    </arguments>
</block>
```
