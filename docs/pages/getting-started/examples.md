# Examples

Each example starts with a task and shows the Magento files needed to
complete it. If Magewire is new to you, build the counter first; it uses
one component class, one PHTML template, and one layout file.

## Tutorials

| Build | What you will use |
|---|---|
| [A counter](../../index.md#quickstart) | Component, template, and layout binding |
| [A customer-name form](../html-directives/wire-submit.md#save-a-customer-name) | Deferred model state, submit action, server validation, repository |
| [Two components that communicate](../essentials/events.md) | `dispatch()` and `#[On]` |
| [A paginated list](../features/pagination.md#add-pagination-to-a-component) | `WithPagination`, page controls, last-page boundary |
| [A Hyvä compatibility module](../theming/compatibility-module.md) | Composer packaging, layout extension, Alpine, CSP fragment |
| [A Breeze storefront integration](../theming/breeze.md) | Package installation, reusable component, Breeze-only morph hook |
| [An admin editor](../admin/building-admin-components.md) | Admin layout, ACL, application service |
| [Magento flash messages](examples/magento-flash-messages.md) | A Magewire feature and the Hyvä browser bridge |

The examples use `Vendor_Module` as a placeholder for your enabled Magento
module. Replace it with your module name and check that the matching
storefront or admin integration is installed.

<a id="ecosystem-note"></a>
<a id="developer-tooling"></a>
<a id="magewire-agent-skills"></a>
<a id="magento-bricklayer-third-party"></a>

## Try a complete interaction

After adding the [counter](../../index.md#quickstart), open your CMS home
page and click **Increase**. The browser should send a Magewire update
request and change the count without navigating. A
[Playwright check](../essentials/testing.md#test-an-application-component)
shows how to verify that behavior in a project.

When adapting another example, keep its PHP logic in a Magento service
when a controller, queue consumer, or second component needs the same rule.
Keep only theme-specific browser and styling code in a
[compatibility module](../theming/compatibility-module.md).

<a id="packages"></a>

## Choose an integration package

| Area | Package |
|---|---|
| Hyvä storefront | [`magewirephp/magewire-hyva-theme`](../theming/index.md#hyva-storefront) |
| Breeze storefront | [`swissup/module-breeze-magewire`](../theming/breeze.md) |
| Existing Hyvä Checkout V1 components | [`magewirephp/magewire-hyva-checkout`](../theming/hyva-checkout-bc.md) |
| Magento Admin | [`magewirephp/magewire-admin`](../admin/installation.md) |

For a theme without an integration package, start with the
[compatibility-module guide](../theming/compatibility-module.md).
