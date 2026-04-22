# Hydration

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/hydration") }}

## Update endpoint

Magewire posts snapshots to `/magewire/update`. The checksum is an HMAC signed with the Magento crypt key (`app/etc/env.php` → `crypt/key`).

## Built-in synthesizers

Magewire adds a `\Magento\Framework\DataObject` synthesizer on top of the default scalars, arrays, `\stdClass`, and backed enums. Custom types require a synthesizer registered in `etc/frontend/di.xml`. See [Synthesizers](../advanced/synthesizers.md).

## Hydration hooks

Re-resolve non-serialisable Magento dependencies after a property is restored:

```php
public int $productId = 0;

private ?ProductInterface $product = null;

public function hydrateProductId(int $value): void
{
    $this->product = $this->productRepository->getById($value);
}
```
