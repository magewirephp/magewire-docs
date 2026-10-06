# Actions

An action is a public method on a Magewire component. A directive such as
`wire:click` or `wire:submit` calls it on the server, then Magewire renders the
component again.

<a id="defining-an-action"></a>

## Call a method from PHTML

This counter accepts a step size, but keeps the allowed range on the server:

```php title="Magewire/StepCounter.php"
<?php

namespace Vendor\Module\Magewire;

use Magento\Framework\Exception\LocalizedException;
use Magewirephp\Magewire\Component;

class StepCounter extends Component
{
    public int $count = 0;

    public function add(int $step = 1): void
    {
        if ($step < 1 || $step > 10) {
            throw new LocalizedException(__('Choose a step from 1 to 10.'));
        }

        $this->count += $step;
    }
}
```

```php title="view/frontend/templates/magewire/step-counter.phtml"
<div>
    <span><?= $escaper->escapeHtml(__('Count: %1', $magewire->count)) ?></span>
    <button type="button" wire:click="add(1)" wire:loading.attr="disabled" wire:target="add">
        <?= $escaper->escapeHtml(__('+1')) ?>
    </button>
    <button type="button" wire:click="add(5)" wire:loading.attr="disabled" wire:target="add">
        <?= $escaper->escapeHtml(__('+5')) ?>
    </button>
</div>
```

The two buttons call the same reusable action. `wire:loading.attr="disabled"`
prevents repeated clicks while it runs. The method still checks `$step` because
browser-supplied arguments can be changed outside the template.

## Only your own public methods are actions

The browser can call any public method defined on your component, even one no template uses. Keep helpers
`protected` or `private`.

Methods inherited from Magewire's `Component` and `Component\Form`, such as `reset`, `redirect`, and `validate`, are
not actions, and neither are [lifecycle hooks](lifecycle-hooks.md#hooks-are-not-actions). To let the browser use one,
wrap it in an action of your own:

```php
public function clearSearch(): void
{
    $this->reset('query');
}
```

```php
<button type="button" wire:click="clearSearch"><?= $escaper->escapeHtml(__('Clear')) ?></button>
```

!!! danger "Upgrade to 3.7.2"
    Magewire 3.0.0 through 3.7.1 also accepted browser calls to inherited methods
    ([GHSA-64j9-rg74-hqc7](https://github.com/magewirephp/magewire/security/advisories/GHSA-64j9-rg74-hqc7)).
    See [Security](../advanced/security.md#browser-callable-methods).

<a id="authorisation"></a>

## Authorize data-changing work

Keep persistence in a Magento service that other entry points can reuse. The
component owns interaction and authorization; the service owns the business
operation and checks the target again:

```php title="Magewire/Admin/ArchiveRecord.php"
<?php

namespace Vendor\Module\Magewire\Admin;

use Magento\Framework\AuthorizationInterface;
use Magento\Framework\Exception\AuthorizationException;
use Magewirephp\Magewire\Component;
use Vendor\Module\Model\RecordArchiver;

class ArchiveRecord extends Component
{
    public function __construct(
        private readonly AuthorizationInterface $authorization,
        private readonly RecordArchiver $archiver
    ) {
    }

    public function archive(int $recordId): void
    {
        if (! $this->authorization->isAllowed('Vendor_Module::archive')) {
            throw new AuthorizationException(__('You cannot archive this record.'));
        }

        // RecordArchiver must load the record and check its business rules.
        $this->archiver->archive($recordId);
    }
}
```

`Vendor_Module::archive` is an ACL resource declared by your module.
`RecordArchiver` is an application service you provide; it should reload the
record by ID rather than trusting component state. The same service can be
used by a controller, queue consumer, or another component.

Use `boot()` for a check that applies to every request made by a component.
Still check individual actions when they require a stronger permission.
See [Security](../advanced/security.md) for the request boundary.

## Rate limiting

Magewire's request rate limiting can reduce abusive traffic. It does not
replace input validation or authorization. See
[Rate limiting](../features/rate-limiting.md).
