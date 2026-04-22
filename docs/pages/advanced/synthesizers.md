# Synthesizers

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/synthesizers") }}

## Built-in synthesizers

Magewire adds a `\Magento\Framework\DataObject` synthesizer on top of Livewire's defaults (scalars, arrays, `\stdClass`, backed enums).

## Writing a custom synthesizer

```php title="Vendor/Module/Magewire/Synthesizers/MoneySynth.php"
<?php

namespace Vendor\Module\Magewire\Synthesizers;

use Vendor\Module\Model\Money;

class MoneySynth extends \Magewirephp\Magewire\Mechanisms\HandleComponents\Synthesizers\Synth
{
    public static string $key = 'mny';

    public static function match($target): bool
    {
        return $target instanceof Money;
    }

    public function dehydrate(Money $target): array
    {
        return [
            ['amount' => $target->amount(), 'currency' => $target->currency()],
            [],
        ];
    }

    public function hydrate($value): Money
    {
        return new Money($value['amount'], $value['currency']);
    }
}
```

## Registering via area-scoped DI

Register in `etc/frontend/di.xml` (and `etc/adminhtml/di.xml` where used) — never global `etc/di.xml`:

```xml title="etc/frontend/di.xml"
<type name="Magewirephp\Magewire\Mechanisms\HandleComponents\HandleComponents">
    <arguments>
        <argument name="synthesizers" xsi:type="array">
            <item name="money" xsi:type="string">Vendor\Module\Magewire\Synthesizers\MoneySynth</item>
        </argument>
    </arguments>
</type>
```

## What not to synthesize

Never expose Magento services, repositories, connections, or anything referencing `ObjectManager` as public properties. Inject via the constructor instead.
