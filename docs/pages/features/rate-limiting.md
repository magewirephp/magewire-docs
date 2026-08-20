# Rate Limiting

Magewire can throttle update traffic with a cache-backed sliding window. It is **disabled by default** and configured at:

```text
Stores → Configuration → Advanced → Magewire → Features → Rate Limiting
```

Public component methods still require authorization and input validation. Rate limiting limits volume; it does not make an unsafe action secure.

## Variants

The variants are mutually exclusive:

| Variant | Enforcement | Budget |
|---|---|---|
| None | No rate limiting. This is the default. | — |
| Requests only | Runs once in the 3.5 request-filter pipeline, before component reconstruction. | Configurable maximum and decay window. |
| Components only | Runs for each reconstructed component. | Fixed at 4 attempts per 5 seconds in Magewire 3.5. |

The component variant currently has no per-component attribute or configurable component-specific budget. The admin field description may suggest otherwise, but the 3.5 runtime uses the fixed budget above.

## Request scope

For the request variant:

- **Shared** uses one budget for the request fingerprint. A bundled request consumes one attempt regardless of component count.
- **Isolated** maintains a budget per component identifier. Each component in a bundled request consumes its own attempt, and one exhausted component rejects the request.

`Max Attempts` and `Decay Seconds` configure the sliding window for this variant.

Rate limiting is always evaluated in production mode. In default or developer mode it is skipped unless **Enable in Developer Mode** is set to Yes.

## Rejection behavior

A rejected request receives HTTP 429. Magewire's request-filter bridge marks its short customer-facing message with `X-Magewire-Message-Severity`, allowing a theme notifier—or a browser alert fallback—to present it safely. Generic server error bodies and stack traces do not receive that marker.

The core feature does not provide a log-only mode and does not write special `MagewireRateLimit` entries. Use your infrastructure metrics, Magento logging extension, or a custom request filter when additional observability is required.

## Related

- [Request Filters](../advanced/request-filters.md)
- [Actions](../essentials/actions.md)
- [Security](../advanced/security.md)
