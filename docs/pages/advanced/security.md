# Security

Treat a Magewire action like a Magento controller action: the browser chooses
the method arguments and supplies public component state. The snapshot
checksum protects integrity, but an action still needs its own access and
business checks.

<a id="browser-callable-methods"></a>

## What the browser can call

Every public method defined on your component class, or on your own base classes and traits, is an action. The
browser can call it with any arguments, even when no template refers to it. Keep helpers `protected` or `private`,
and check access inside each action.

Since 3.7.2, Magewire rejects browser calls to:

- public methods inherited from `Magewirephp\Magewire\Component` or `Component\Form` and their traits, such as
  `reset`, `fill`, `redirect`, `validate`, and `tap`;
- methods whose name starts with `__`;
- lifecycle hooks and other [reserved names](../getting-started/releases/upgrade-notes.md#reserved-method-names),
  such as `mount`, `boot`, `placeholder`, and `updatedEmail`.

The same rules apply to [event listener](../essentials/events.md#listener-targets) targets. To expose a framework
helper, wrap it in a public action that performs your checks. Re-declaring an inherited method as `public` on your
component makes it callable again.

!!! danger "Magewire 3.0.0 to 3.7.1"
    Earlier releases allowed the browser to call the inherited methods listed above
    ([GHSA-64j9-rg74-hqc7](https://github.com/magewirephp/magewire/security/advisories/GHSA-64j9-rg74-hqc7)).
    Upgrade to 3.7.2 or later. See [Upgrade notes](../getting-started/releases/upgrade-notes.md#371-to-372).

## CSRF

Magento's `FormKey` protects every Magewire request automatically. The browser sends it as the top-level `_token`
field in the POST request envelope. The router exposes it to the form-key validator as `token` and removes it from the
component payload; it is not stored inside the serialized snapshot. Magewire rejects requests with a missing or stale
key. Do not disable `FormKey` on the Magewire route.

## Snapshot checksum

Each snapshot carries an HMAC checksum signed with the Magento crypt key (`app/etc/env.php` → `crypt/key`). The checksum authenticates the snapshot's integrity; it does not authorise the user. Always check permissions inside actions.

Public properties are browser-controlled state. Magewire 3.7 does not provide a documented locked-property attribute,
so do not rely on an identifier being absent from the template or lacking `wire:model`. Reload sensitive entities in
the action, validate the current user against the exact target, and keep authorization in the service that performs
the write.

## Namespace and escaping

Components extend `Magewirephp\Magewire\Component`. In templates the instance is available as `$magewire`; use Magento's `$escaper` for every output:

```php
<p><?= $escaper->escapeHtml($magewire->bio) ?></p>
<a href="<?= $escaper->escapeUrl($magewire->link) ?>">…</a>
<img alt="<?= $escaper->escapeHtmlAttr($magewire->caption) ?>" src="…" />
```

For inline JavaScript, use a
[Script fragment](../concepts/fragments.md#the-script-fragment) and encode
dynamic values for their actual JavaScript context. A raw `<script>` in a
component template bypasses Magewire's CSP handling.

## Authorisation

Use Magento's authorization service in public methods, and `boot()` for up-front guards:

```php
public function refund(int $orderId): void
{
    if (! $this->authorization->isAllowed('Vendor_Module::refund')) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Not allowed.'));
    }

    // The service loads the order and checks the requested operation.
    $this->refundService->refund($orderId);
}

public function boot(): void
{
    if (! $this->customerSession->isLoggedIn()) {
        throw new \Magento\Framework\Exception\AuthorizationException(__('Login required.'));
    }
}
```

Declare `Vendor_Module::refund` in your module's `etc/acl.xml`. The service
must verify the exact order and refund rules; an ACL check alone does not
make an arbitrary browser-supplied ID safe.

## Rate limiting

Magewire ships `SupportMagewireRateLimiting`, disabled by default. Enable the appropriate request or component variant per scope after choosing a budget suitable for the application. See [Rate Limiting](../features/rate-limiting.md).

Use [Request Filters](request-filters.md) for inexpensive request-wide checks that must run before component reconstruction. Filters complement, not replace, authorization inside actions.

## Vulnerability reports

Report suspected Magewire vulnerabilities privately to `magewirephp@wpoortman.nl` according to the repository security policy. Do not post exploit details in a public issue, discussion, or pull request.

## Security advisories

Published fixes are listed under the repository's
[security advisories](https://github.com/magewirephp/magewire/security/advisories). Each advisory names the affected
and fixed releases. Upgrade every environment, including staging, development, and test installations, and check
lockfiles and deployment images as well as `composer.json`.

| Advisory | Severity | Affected | Fixed |
|---|---|---|---|
| [GHSA-64j9-rg74-hqc7](https://github.com/magewirephp/magewire/security/advisories/GHSA-64j9-rg74-hqc7): browser access to framework component methods | High | 3.0.0 – 3.7.1 | 3.7.2 |

## CSP

Magewire's bundle ships the CSP build of Alpine. Inline scripts go through the [fragment](../concepts/fragments.md) system; never emit a raw `<script>` tag from a component template.
