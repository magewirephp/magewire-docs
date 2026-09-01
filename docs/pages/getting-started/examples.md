# Examples

## Tutorials

Walkthroughs that build something real and, where relevant, show what it takes to adapt a Livewire
concept to Magento.

- [Magento Flash Messages](examples/magento-flash-messages.md): surface typed messages from a
  component, and see how a Laravel/Livewire feature is re-seated on Magento's primitives.

## Ecosystem note

The public `magewirephp/magewire-examples` and `magewirephp/magewire-requirejs` repositories currently target Magewire 1. Treat them as historical references, not Magewire 3 starter projects.

## Developer tooling

### Magewire agent skills

The official [`magewirephp/magewire-skills`](https://github.com/magewirephp/magewire-skills) repository provides portable agent skills for Magewire 3 development. It covers day-to-day component work, architecture, backwards compatibility, best practices, JavaScript, Portman, and theme integrations. Install only the skill directories your coding agent needs.

### Magento Bricklayer (third-party)

[Magento Bricklayer](https://github.com/Inchoo/magento-bricklayer) is a third-party, AI-assisted Magento development toolkit maintained by Inchoo. Its MCP server gives supported coding agents runtime visibility into Magento configuration, DI, plugins, events, layouts, and other installation-specific state. It also bundles a Magewire 3 skill family covering architecture, backwards compatibility, best practices, JavaScript, Portman, and theming.

Install it as a development dependency and follow the repository's setup instructions for your coding agent:

```bash
composer require --dev inchoo/magento-bricklayer
```

Bricklayer is not maintained by MagewirePHP. Check its Magento and PHP requirements, security model, and release notes before enabling it in a project.

## Packages

In addition to the Magewire core, there are several other MagewirePHP packages that may be of interest.

| Package | Purpose | Repository |
|---|---|---|
| `magewirephp/magewire-hyva-theme` | Hyvä storefront compatibility | [magewire-hyva-theme](https://github.com/magewirephp/magewire-hyva-theme) |
| `magewirephp/magewire-hyva-checkout` | Hyvä Checkout compatibility | [magewire-hyva-checkout](https://github.com/magewirephp/magewire-hyva-checkout) |
| `magewirephp/magewire-admin` | Magento admin integration | [magewire-admin](https://github.com/magewirephp/magewire-admin) |
| `magewirephp/magewire-fpc` | Experimental full-page-cache integration | [magewire-fpc](https://github.com/magewirephp/magewire-fpc) |

Check each package's Composer constraints and release tags before installation; companion package versions do not imply that every minor release matches the core's minor version.
