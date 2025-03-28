# Magewire PHP

!!! danger "Alpha release"
    **Do not use Magewire V3 in production, as its stability, security, and overall reliability cannot be guaranteed.
    The framework is still in an alpha phase, and breaking changes may occur without warning.
    Using it in a live environment is entirely at your own risk and may lead to unexpected issues, including potential
    security vulnerabilities and system instability.**

    [:fontawesome-solid-arrow-up-right-from-square: More Details](pages/getting-started/alpha.md){ .md-button .md-button--danger }

Welcome to the official documentation for Magewire PHP. This guide provides all the necessary information to get started
with Magewire V3, understand its core concepts, and build dynamic Magento applications using Livewire-like components.

!!! info "Understanding Magewire Documentation and Its Relation to Livewire"
    Magewire is heavily inspired by Livewire, and as a result, most of its core functionality works in the same way.
    For this reason, all essential documentation can be found in the official [Livewire documentation](https://livewire.laravel.com/docs/quickstart).
    The Magewire documentation primarily focuses on Magento-specific implementations, custom features,
    and additional explanations that are either missing from the Livewire docs or are not relevant due to platform differences.
    If you're looking for a deeper understanding of how Magewire works under the hood, we highly recommend referring to the
    Livewire documentation alongside this guide.

## What is Magewire?

MagewirePHP is a powerful framework for Magento 2 that enables developers to build reactive and dynamic user interfaces
without writing JavaScript. It is inspired by [Laravel Livewire](https://livewire.laravel.com/) and offers a similar
development experience within the Magento ecosystem.

Magewire comes with [Alpine JS](https://alpinejs.dev/) preloaded as the primary JavaScript engine behind the framework.
If you are using Alpine JS within your theme, make sure to disable your version to prevent it from being loaded twice,
as this can cause conflicts.

Each theme should have its own submodule on top of Magewire to ensure compatibility. Theme-specific modifications,
such as custom events and loading files, are required for proper functionality. By default, Magewire is built on the [Hyvä theme](https://www.hyva.io/),
but this integration can easily be disabled, as it is a separate compatibility module rather than part of the core architecture.

!!! warning "Security Vulnerabilities"
    If you discover a security vulnerability within Magewire, please create a [merge request](https://github.com/magewirephp/magewire/pulls)
    or an [discussion](https://github.com/magewirephp/magewire/discussions). All security vulnerabilities will be promptly addressed.

## Requirements

Before we start, make sure you have the following installed:

- Magento version 2.4.4 or later
- PHP version 8.1 or later

## Installation

To install Magewire in your Magento 2 project, follow these steps:

1. Require Magewire via Composer:
   ```sh
   composer require magewirephp/magewire
   ```
2. Enable the module:
   ```sh
   bin/magento module:enable Magewirephp_Magewire
   ```
3. Enable the theme compatibility module (determined per theme, in this case Hyvä):
   ```sh
   bin/magento module:enable Magewirephp_MagewireCompatibilityWithHyva
   ```

4. Run the setup upgrade command:
   ```sh
   bin/magento setup:upgrade
   ```
5. Deploy static content (when in production mode):
   ```sh
   bin/magento setup:static-content:deploy
   ```
6. Flush the cache:
   ```sh
   bin/magento cache:flush
   ```

## Quickstart Guide

!!! info "Details"
    This quickstart guide does not cover all the details behind the "why" and "how" but is intended to provide a concise
    overview of creating a basic Layout XML-driven Magewire component.

Let's create a simple Magewire component to demonstrate its basic capabilities.

{{ include("create-a-component.md") }}

Congratulations! You have successfully created your first Magewire component.

When you click the button, you'll notice the count updates instantly without a full page reload.
This is the power of Magewire—seamless, dynamic frontend interactions built entirely in PHP.

We've only scratched the surface of what Magewire can do. Continue exploring the documentation to unlock its full potential!

!!! info "Full Page Cache (FPC)"
    Since a Magewire component's state is determined by the JSON objects bound to the component, cached pages will
    naturally retain the cached state rather than the most recent one. As of now, there is no definitive solution,
    though some experimental approaches are being explored. The most viable option currently is using wire:init to load
    the state on page load, though this requires an XHR request when the component is initialized.

## Next Steps

- [Contribute](pages/getting-started/contribute.md)
- [Documentation](pages/getting-started/documentation.md)
- [Examples](pages/getting-started/examples.md)
- [License](pages/getting-started/license.md)
- [Purpose](pages/getting-started/purpose.md)
- [Sponsors](pages/getting-started/sponsoring)
- [Upgrade](pages/getting-started/upgrade.md)
- [Architecture](pages/getting-started/architecture/index.md)

For further details, visit the [MagewirePHP GitHub Repository](https://github.com/magewirephp/magewire).
