# Admin Rate Limiting

Magewire's rate-limiting Feature (`SupportMagewireRateLimiting`) is active in the admin just like on the storefront. `magewire-admin` ships an admin-specific template so the rate-limit response renders inside the admin's layout.

## Why it matters in admin

The admin panel is a higher-value target than the storefront — a compromised admin account can read customer PII, refund orders, or change prices. Rate limiting caps the number of requests a component can receive per unit of time, protecting against both brute-force attacks (an attacker scripting an admin UI) and runaway loops from buggy code.

## Admin-specific template

The admin layout includes a dedicated rate-limit message template:

```xml title="magewire-admin/view/adminhtml/layout/default.xml"
<referenceBlock name="magewire.features.support-magewire-rate-limiting"
    template="Magewirephp_MagewireAdmin::magewire-features/support-magewire-rate-limiting/support-magewire-rate-limiting.phtml"/>
```

The block `magewire.features.support-magewire-rate-limiting` already exists in the core layout; the admin package just overrides its template via `referenceBlock` so rate-limit errors render with admin-theme chrome instead of the storefront toast.

## Configuration

Rate limiting is configured from the Magento admin:

```
Stores → Configuration → Advanced → Magewire → Rate Limiting
```

The storefront and admin share the same configuration surface — thresholds apply to both unless overridden per component.

## Per-component override

A component that needs a tighter limit (a password-reset form, an import action) can declare its own threshold with the rate-limit attribute — see the core [Rate limiting](../features/rate-limiting.md) page.

## When to tighten

| Action | Suggested max |
|---|---|
| Bulk import / export | 1 request per minute |
| Refund / credit memo | 5 per minute |
| Password resets | 3 per minute |
| Generic grid filtering | Default (per config) |

Err on the side of lower limits — admin users rarely legitimately exceed them, and the feedback pressure from hitting a limit is small compared to the cost of a compromised account running unchecked.

## Related

- [Rate limiting (core)](../features/rate-limiting.md)
- [Security](../advanced/security.md)
- [How it works](how-it-works.md)
