# Magewire PHP 3

!!! danger "Security release: upgrade to Magewire 3.7.2"
    Security advisory
    [GHSA-64j9-rg74-hqc7](https://github.com/magewirephp/magewire/security/advisories/GHSA-64j9-rg74-hqc7)
    (High) affects Magewire 3.0.0 through 3.7.1. A visitor who can load a page with a Magewire component could call
    public methods inherited from Magewire's base component that the component never exposed as actions.

    Upgrade every environment to 3.7.2, including production, staging, development, local, demo, and test
    installations. Agencies should also check client projects, lockfiles, and deployment images.

    ```shell
    composer update magewirephp/magewire:3.7.2 --with-all-dependencies
    composer show magewirephp/magewire
    ```

    Custom components that call inherited Magewire helpers from the browser or from event listeners may need a small
    change. See [Upgrade notes](pages/getting-started/releases/upgrade-notes.md#371-to-372).

Build interactive Magento interfaces with PHP and PHTML. A Magewire component
starts as a Magento layout block, renders a template, and responds to browser
events through a PHP class. Magewire updates the rendered HTML without a full
page reload.

You can begin with a counter, then use the same pattern for search filters,
forms, account tools, or checkout steps. Business logic stays in ordinary
Magento services, so multiple components and themes can reuse it.

Magewire 3 uses parts of [Livewire 3](https://livewire.laravel.com/docs/3.x/).
These guides show the files and APIs that work in Magento. A ported Livewire
class alone does not mean its feature is active; see
[How to use these docs](pages/getting-started/documentation.md) when adapting
an upstream example.

## Requirements

Before installing, check:

- PHP 8.2 or newer;
- Magento Open Source or Mage-OS with a Magento 2.4.6-compatible framework or newer;
- a theme integration for the area where your component renders.

For exact platform combinations, consult the
[core production-build matrix](https://github.com/magewirephp/magewire/blob/main/.github/workflows/production-build.yml)
for the release you install.

## Installation

Install the core module in your Magento project:

```shell
composer require magewirephp/magewire
bin/magento module:enable Magewirephp_Magewire
bin/magento setup:upgrade
```

For a Hyvä storefront, add the maintained theme integration:

```shell
composer require magewirephp/magewire-hyva-theme
bin/magento module:enable Magewirephp_MagewireHyvaTheme
bin/magento setup:upgrade
```

For Magento Admin, install
[`magewirephp/magewire-admin`](pages/admin/installation.md). Existing Hyvä
Checkout components built for Magewire V1 need the separate
[checkout compatibility package](pages/theming/hyva-checkout-bc.md).
For Breeze storefronts, use the
[`swissup/module-breeze-magewire` integration](pages/theming/breeze.md).

After deploying static content in production mode, clean the Magento caches:

```shell
bin/magento setup:static-content:deploy
bin/magento cache:clean
```

See [Theming](pages/theming/index.md) for other theme integrations and [Admin](pages/admin/index.md) for the separate admin package.

## Quickstart

This complete example adds a counter to the CMS home page. It uses an existing
`Vendor_Module` module; replace the vendor and module names with yours.

{{ include("create-a-component.md") }}

When the counter works, continue with [Basics](pages/getting-started/basics.md)
to pass initial values from layout XML and understand each request.

## A form in one glance

The same component pattern works for a form. A plain `wire:model` binding
waits for the next action; `wire:submit` calls a public PHP method with the
current values:

```php title="view/frontend/templates/magewire/contact.phtml"
<form wire:submit="save">
    <label for="contact-email"><?= $escaper->escapeHtml(__('Email')) ?></label>
    <input id="contact-email" type="email" wire:model="email">

    <button type="submit" wire:loading.attr="disabled">
        <?= $escaper->escapeHtml(__('Save')) ?>
    </button>
</form>
```

See [`wire:model`](pages/html-directives/wire-model.md) and
[`wire:submit`](pages/html-directives/wire-submit.md) for the matching PHP
action, validation, and progress state.

## Alpine.js and themes

Magewire's browser runtime includes Alpine.js. Use the
[Hyvä theme package](pages/theming/index.md) when building for Hyvä. For
Breeze, use its [integration package](pages/theming/breeze.md). For a theme
without an integration package, create a
[compatibility module](pages/theming/compatibility-module.md) that coordinates
script loading and your theme's frontend conventions.

## Full-page cache

Cached HTML can contain an old component snapshot. Use
[lazy loading](pages/features/lazy-loading.md) or
[`wire:init`](pages/html-directives/wire-init.md) when data must be fetched
after page load, and test behavior with your store's full-page cache enabled.

## Support and security

Use the [Magewire GitHub repository](https://github.com/magewirephp/magewire) for public bug reports and discussions.

!!! danger "Report vulnerabilities privately"
    Do not open a public issue, discussion, or pull request for a suspected security vulnerability. Follow the repository's security policy and email `magewirephp@wpoortman.nl`.

Published fixes are listed under the repository's
[security advisories](https://github.com/magewirephp/magewire/security/advisories). Each advisory names the affected
and fixed releases; upgrade to the fixed release or later.

## Next steps

- [How to use these docs](pages/getting-started/documentation.md): find a guide for your task.
- [Components](pages/essentials/components.md): pass layout arguments and reuse a class.
- [Compatibility module](pages/theming/compatibility-module.md): package theme integration for reuse.
- [V3 versus V1](pages/getting-started/v3-vs-v1.md): understand the runtime and migration differences.
- [Lazy loading](pages/features/lazy-loading.md): defer expensive components.
- [Application container](pages/advanced/application-container.md): resolve Magento services from ported or extension code.
- [Architecture](pages/advanced/architecture/index.md): explore mechanisms, features, and extension points.
