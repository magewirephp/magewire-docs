# Magewire PHP - V3

!!! danger "Beta release"
    **Do not use Magewire V3 in production, as its stability, security, and overall reliability cannot be guaranteed.
    The framework is still in an beta phase, and breaking changes may occur without warning.
    Using it in a live environment is entirely at your own risk and may lead to unexpected issues, including potential
    security vulnerabilities and system instability.**

    Please refer to the [beta](pages/getting-started/beta.md) page for more details.

{{ include("admonition/documentation-under-construction.md") }}

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

### So Much More

Both [Livewire](https://livewire.laravel.com/) and Magewire are known for their dynamic capabilities powered by XHR (AJAX) requests.
This can sometimes be intimidating, as making a full server round trip just to update a small piece of HTML may seem
excessive—let alone concerns about potential deadlocks or other pitfalls.

However, Magewire is much more than just a framework that standardizes XHR requests and morphs returned HTML into the existing DOM.
It's a powerful and feature-rich framework that caters to both backend and frontend developers.
Its seamless integration with [Alpine JS](https://alpinejs.dev/) makes the two feel like a natural pair.

Magewire isn't limited to dynamic interactivity alone. It offers a wide range of possibilities and use cases—many of
which you'll only begin to appreciate as you explore its full potential.

You can learn more about the purpose of Magewire [here](pages/getting-started/purpose.md).

## Requirements

Before we start, make sure you have the following installed:

- Magento 2.4.4 or later
- PHP 8.1 or later

## Installation

To install Magewire in your Magento 2 project, follow these steps:

1. Require Magewire via Composer:
   ```shell
   composer require magewirephp/magewire
   ```
2. Enable the module:
   ```shell
   bin/magento module:enable Magewirephp_Magewire
   ```
3. Enable the theme compatibility module (determined per theme, in this case Hyvä):
   ```shell
   bin/magento module:enable Magewirephp_MagewireCompatibilityWithHyva
   ```
4. Run the setup upgrade command:
   ```shell
   bin/magento setup:upgrade
   ```
5. Deploy static content (when in production mode):
   ```shell
   bin/magento setup:static-content:deploy
   ```
6. Flush the cache:
   ```shell
   bin/magento cache:flush
   ```

## Quickstart

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

## Support

!!! warning "Security Vulnerabilities"
    If you discover a security vulnerability within Magewire, please create a [merge request](https://github.com/magewirephp/magewire/pulls)
    or an [discussion](https://github.com/magewirephp/magewire/discussions). All security vulnerabilities will be promptly addressed.

Magewire is a fully open-source project, meaning support is provided voluntarily by its contributors and the surrounding community.

To request support, you can start a discussion or open an issue on our [GitHub Repository](https://github.com/magewirephp/magewire).

## Next Steps

With Magewire, there are a few key concepts worth understanding if you want to go beyond the basics—like binding a `magewire` argument to a block via Layout XML.

|                                                                  | Description                                                                                                                                                                                     |
|------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Resolvers](pages/advanced/architecture/mechanisms/resolvers.md) | While Magewire supports various methods for binding components to blocks, some scenarios require custom handling. For those, an API is available to help you tailor the solution to your needs. |
| [Portman](pages/advanced/architecture/portman.md)                | To contribute to Magewire, it's important to understand the idea behind Portman. We've provided extensive documentation to guide you and help you get up to speed quickly.                      |

Some other great resources to get you started are:

- [Basics](pages/getting-started/basics.md)
- [Examples](pages/getting-started/examples.md)
- [FAQ](pages/getting-started/faq.md)
- [Notables](pages/getting-started/notables.md)
- [Upgrade](pages/getting-started/upgrade.md)
- [Architecture](pages/advanced/architecture/index.md)

For further details, visit the [MagewirePHP GitHub Repository](https://github.com/magewirephp/magewire).
