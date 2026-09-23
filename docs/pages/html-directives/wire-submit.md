# wire:submit

Use `wire:submit` on a form to call a PHP action without a full page reload.
Magewire prevents the browser's normal form submission and sends the current
`wire:model` values with the action.

## Save a customer name

This example belongs on a customer account page. It loads the current name
on the first render, checks the logged-in customer on every request, and
saves through Magento's customer repository.

```php title="Magewire/AccountName.php"
<?php

namespace Vendor\Module\Magewire;

use Magento\Customer\Api\CustomerRepositoryInterface;
use Magento\Customer\Model\Session as CustomerSession;
use Magento\Framework\Exception\AuthorizationException;
use Magewirephp\Magewire\Component;

class AccountName extends Component
{
    public string $firstName = '';
    public string $error = '';

    public function __construct(
        private readonly CustomerSession $customerSession,
        private readonly CustomerRepositoryInterface $customers
    ) {
    }

    public function boot(): void
    {
        if (! $this->customerSession->isLoggedIn()) {
            throw new AuthorizationException(__('Please sign in first.'));
        }
    }

    public function mount(): void
    {
        $customer = $this->customers->getById((int) $this->customerSession->getCustomerId());
        $this->firstName = (string) $customer->getFirstname();
    }

    public function save(): void
    {
        $name = trim($this->firstName);

        if ($name === '' || mb_strlen($name) > 50) {
            $this->error = (string) __('Enter a name of 1 to 50 characters.');
            return;
        }

        $customer = $this->customers->getById((int) $this->customerSession->getCustomerId());
        $customer->setFirstname($name);
        $this->customers->save($customer);

        $this->firstName = $name;
        $this->error = '';
        $this->magewireNotifications()->make(__('Name saved.'))->asSuccess();
    }
}
```

The action reloads the customer using the current session ID. It never
accepts a customer ID from the browser. For a larger workflow, move
validation and persistence into a Magento service that other entry points
can use too.

```php title="view/frontend/templates/magewire/account-name.phtml"
<form wire:submit="save">
    <label for="account-first-name">
        <?= $escaper->escapeHtml(__('First name')) ?>
    </label>
    <input id="account-first-name"
           name="first_name"
           type="text"
           wire:model="firstName"
           value="<?= $escaper->escapeHtmlAttr($magewire->firstName) ?>">

    <?php if ($magewire->error !== ''): ?>
        <p role="alert"><?= $escaper->escapeHtml($magewire->error) ?></p>
    <?php endif ?>

    <button type="submit" wire:loading.attr="disabled" wire:target="save">
        <?= $escaper->escapeHtml(__('Save')) ?>
    </button>
    <span wire:loading wire:target="save">
        <?= $escaper->escapeHtml(__('Saving…')) ?>
    </span>
</form>
```

Bind the class and template using the same layout argument as any other
component:

```xml title="view/frontend/layout/customer_account_edit.xml"
<referenceContainer name="content">
    <block name="vendor.module.account-name"
           template="Vendor_Module::magewire/account-name.phtml">
        <arguments>
            <argument name="magewire" xsi:type="object" shared="false">
                Vendor\Module\Magewire\AccountName
            </argument>
        </arguments>
    </block>
</referenceContainer>
```

The layout snippet sits inside the usual `<page><body>…</body></page>` file.
Magento's account edit page already has its own form, so place this block
deliberately in a suitable container or account tab for your storefront.

## While the request runs

Magewire temporarily disables form controls during submission. The
`wire:loading` elements above make the state visible and
`wire:loading.attr="disabled"` prevents repeated saves. A client-side
`required` attribute is helpful feedback, but the PHP action still validates
the value before persistence. Magewire does not register Livewire's form
object or `#[Validate]` feature in the current runtime.

See [`wire:model`](wire-model.md) for when input changes reach the server and
[Actions](../essentials/actions.md) for authorization patterns.
