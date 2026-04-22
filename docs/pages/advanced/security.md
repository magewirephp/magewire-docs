# Security

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/security") }}

## CSRF

Magento's `FormKey` protects every Magewire request automatically. The key travels with the snapshot on every POST to `/magewire/update`; Magewire rejects requests with a missing or stale key. Do not disable `FormKey` on the Magewire route.

## Snapshot checksum

Each snapshot carries an HMAC checksum signed with the Magento crypt key (`app/etc/env.php` → `crypt/key`). The checksum authenticates the snapshot's integrity — it does not authorise the user. Always check permissions inside actions.

## Namespace and escaping

Components extend `Magewirephp\Magewire\Component`. In templates the instance is available as `$magewire`; use Magento's `$escaper` for every output:

```html
<p><?= $escaper->escapeHtml($magewire->bio) ?></p>
<a href="<?= $escaper->escapeUrl($magewire->link) ?>">…</a>
<img alt="<?= $escaper->escapeHtmlAttr($magewire->caption) ?>" src="…" />
<script>var name = <?= $escaper->escapeJs(json_encode($magewire->name)) ?>;</script>
```

## Authorisation

Use Magento's authorization service in public methods, and `boot()` for up-front guards:

```php
public function refund(int $orderId): void
{
    if (! $this->authorization->isAllowed('Magento_Sales::refund')) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
    }

    $this->refundService->refund($orderId);
}

public function boot(): void
{
    if (! $this->customerSession->isLoggedIn()) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Login required.'));
    }
}
```

## Rate limiting

Magewire ships `SupportMagewireRateLimiting`. Configure thresholds per store from the admin. See [Rate limiting](../features/rate-limiting.md).

## CSP

Magewire's bundle ships the CSP build of Alpine. Inline scripts go through the [fragment](../concepts/fragments.md) system — never emit a raw `<script>` tag from a component template.
