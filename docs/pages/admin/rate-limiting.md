# Admin Rate Limiting

Core rate limiting applies in `adminhtml` as well as the storefront when enabled. Configure it under Magewire's **Features → Rate Limiting** section and choose either the request or component variant described in [Rate Limiting](../features/rate-limiting.md).

## Magewire 3.5 response bridge

The request variant rejects before component reconstruction. Magewire's generic request-filter browser bridge handles customer-safe rejection bodies and uses the notifier when one is available, with an alert fallback otherwise. It is no longer implemented by a rate-limit-specific core layout block.

!!! warning "Current companion-package mismatch"
    The currently tagged `magewirephp/magewire-admin` package still references `magewire.features.support-magewire-rate-limiting`. Core Magewire 3.5 removed that block and now renders `magewire.features.support-magewire-request-filters`. The stale reference does not provide an admin-specific rate-limit template. Check for a newer admin release or patch the integration deliberately; do not rely on the old override.

## Security boundary

Throttling reduces request volume but does not replace Magento ACL checks, admin-session validation, form-key verification, or authorization inside component actions. Use infrastructure-level protection for login and broad abuse controls, then use Magewire throttling for update traffic.

The component variant is fixed at 4 attempts per 5 seconds in Magewire 3.5. The request variant exposes configurable maximum attempts, decay seconds, and shared or isolated scope. There is no per-component rate-limit attribute in this release.
