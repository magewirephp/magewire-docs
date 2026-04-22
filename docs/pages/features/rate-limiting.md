# Rate Limiting

`SupportMagewireRateLimiting` caps the number of requests a component accepts over a sliding window. The feature is on by default and configured from Magento admin.

## Why it exists

Every public method on a component is a public HTTP endpoint. Without a rate limit:

- A brute-force attacker can submit a login form thousands of times per second.
- A malformed client can flood the server with `wire:poll` ticks.
- A runaway Alpine loop can trigger `$wire.set()` in an infinite loop.

Rate limiting caps all of that at the framework level — before the action runs.

## Configuration

```
Stores → Configuration → Advanced → Magewire → Rate Limiting
```

The configuration is shared across the storefront and admin.

| Setting | Meaning |
|---|---|
| Variant | Which rate-limiting strategy to apply (source: `RateLimitingVariant`). |
| Requests → Scope | `shared` (one bucket across all components per session) or `isolated` (per-component bucket). Source: `RequestsScope`. |
| Requests → Max Attempts | Maximum number of requests allowed within the decay window. |
| Requests → Decay Seconds | Time window in seconds after which the attempt counter resets. |

Global settings take precedence over any component-specific limits when both are configured.

## Per-component override

A component can declare tighter limits via DI on `Magewirephp\Magewire\Features\SupportMagewireRateLimiting\UpdateRequestRateLimiter` — see the class and its cache-backed storage (`RateLimiterCacheStorage`) for the current API surface.

## What the user sees

By default, rate-limited requests return an error notification (storefront) or an admin-style toast (admin). The exact rendering is theme-scoped — see [Admin rate limiting](../admin/rate-limiting.md) for the admin path and customise the template per theme if needed.

## Observability

Rate-limit events are logged. Check `var/log/system.log` for `MagewireRateLimit` entries. In log-only mode, hitting the limit logs without rejecting — useful while tuning thresholds.

## Related

- [Actions](../essentials/actions.md)
- [Security](../advanced/security.md)
- [Admin rate limiting](../admin/rate-limiting.md)
