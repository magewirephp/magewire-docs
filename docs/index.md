# Magewire PHP 3

Magewire brings reactive, server-driven components to Magento. Components are PHP classes rendered through Magento layout and `.phtml` templates; browser interactions update them over Magewire requests without a full page reload.

Magewire 3 ports selected parts of [Livewire 3](https://livewire.laravel.com/docs/3.x/) into Magento. This documentation links to Livewire 3 when an API behaves the same and documents Magento integration, Magewire additions, and compatibility differences locally.

!!! warning "Livewire compatibility has boundaries"
    Magewire does not register every class present in its ported Livewire source. A feature is supported only when it appears in these Magewire docs or the Magewire runtime registers it. In particular, do not assume Laravel integrations, form objects, uploads, validation APIs, JavaScript evaluation, or navigation are available merely because Livewire 3 documents them.

## Requirements

Magewire 3 currently requires:

- PHP 8.2 or newer;
- Magento Open Source or Mage-OS with a Magento 2.4.6-compatible framework or newer;
- a theme integration suitable for the storefront or admin area where Magewire runs.

The continuous-integration matrix is the most precise compatibility record. Magewire 3.5 is tested across Magento Open Source 2.4.6 through 2.4.9, Mage-OS 1.3 through 3.2, and PHP 8.2 through 8.5 in compatible combinations.

## Installation

Install and enable the core module:

```shell
composer require magewirephp/magewire
bin/magento module:enable Magewirephp_Magewire
bin/magento setup:upgrade
```

For a Hyvä storefront, install its separate integration package:

```shell
composer require magewirephp/magewire-hyva-theme
bin/magento module:enable Magewirephp_MagewireHyvaTheme
bin/magento setup:upgrade
```

Deploy static content in production mode, then clean the Magento caches:

```shell
bin/magento setup:static-content:deploy
bin/magento cache:clean
```

See [Theming](pages/theming/index.md) for other theme integrations and [Admin](pages/admin/index.md) for the separate admin package.

## Quickstart

The following example creates a component, registers it through Magento layout XML, and renders it from a `.phtml` template.

{{ include("create-a-component.md") }}

Continue with [Basics](pages/getting-started/basics.md) to learn how layout arguments reach component properties and lifecycle methods.

## Alpine.js and themes

Magewire's browser runtime includes Alpine.js. A theme compatibility package is responsible for coordinating that runtime with the theme; the core package is theme-agnostic. Do not remove a theme's Alpine integration globally. Follow the compatibility package's loading strategy so exactly one compatible Alpine instance starts on a page.

## Full-page cache

Cached HTML can contain an old serialized component snapshot. Use lazy loading or `wire:init` when fresh state is required after the page loads. The experimental `magewirephp/magewire-fpc` companion package also provides a dedicated integration for Magewire 3; evaluate it against the caching stack used by your project.

## Support and security

Use the [Magewire GitHub repository](https://github.com/magewirephp/magewire) for public bug reports and discussions.

!!! danger "Report vulnerabilities privately"
    Do not open a public issue, discussion, or pull request for a suspected security vulnerability. Follow the repository's security policy and email `magewirephp@wpoortman.nl`.

## Next steps

- [Documentation model](pages/getting-started/documentation.md): understand what is delegated to Livewire 3 and what is documented locally.
- [V3 versus V1](pages/getting-started/v3-vs-v1.md): understand the runtime and migration differences.
- [Lazy loading](pages/features/lazy-loading.md): defer expensive components.
- [Application container](pages/advanced/application-container.md): resolve Magento services from ported or extension code.
- [Architecture](pages/advanced/architecture/index.md): explore mechanisms, features, and extension points.
