# Component

## Arguments

Since Magewire V3, you can pass arguments to components via block data using the magewire prefix, followed by either a dot (.) or a colon (:) separator.

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

The component looks like:

```php
<?php

class Counter extends Component
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
