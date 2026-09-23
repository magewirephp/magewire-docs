<a id="documentation"></a>

# How to use these docs

Start with [Basics](basics.md) if you have not built a Magewire component yet.
The guide gives you the PHP class, PHTML template, and Magento layout XML you
need to see an update in the browser. From there, [Components](../essentials/components.md)
shows how to reuse the same class on more than one page.

Magewire 3 shares concepts with Livewire 3, but runs in Magento. Every guide
here aims to show the Magento files and the code you can put in them. Links to
[Livewire 3](https://livewire.laravel.com/docs/3.x/) are additional detail for
features that Magewire actually registers.

<a id="documentation-structure"></a>

## Choose a path

| You want to… | Start here |
|---|---|
| Build an interactive storefront block | [Components](../essentials/components.md), then [Properties](../essentials/properties.md) and [Actions](../essentials/actions.md) |
| Build a form | [`wire:model`](../html-directives/wire-model.md) and [`wire:submit`](../html-directives/wire-submit.md) |
| Keep one class reusable across pages | [Layout arguments](../essentials/components.md#pass-initial-values-from-layout) and [Best practices](../advanced/best-practices.md) |
| Integrate a theme | [Theming](../theming/index.md) and [Compatibility module](../theming/compatibility-module.md) |
| Add Magewire to the backend | [Admin installation](../admin/installation.md) and [Building admin components](../admin/building-admin-components.md) |
| Move a V1 component to V3 | [Upgrade](upgrade.md) and [Backwards compatibility](../essentials/backwards-compatibility.md) |

<a id="compatibility-boundary"></a>
<a id="source-verification"></a>

## What "supported" means

The Magewire source contains ported Livewire classes that are not necessarily
active. Check the Magewire component API, area-specific feature registrations,
and companion packages before copying a Livewire example. For instance,
Livewire form objects and its validation feature are not registered in the
current Magewire runtime, even though similarly named code exists in the
source tree. Use a Magento service for validation and persistence.

When a guide describes an integration, install the package named on that page.
The Hyvä theme, Hyvä Checkout compatibility, and admin area each have their
own packages. A storefront example also needs the theme integration used by
your store.

<a id="contributing"></a>
<a id="writing-guidelines"></a>
<a id="using-ai-as-a-writing-aid"></a>

## Contribute an example

A useful documentation example includes the component class, its template,
the layout binding, and any required module or theme setup. Show escaped PHTML
output and an authorization check for public actions that change data. If a
page is unclear or wrong, [contribute a correction](contribute.md) with the
Magewire version and a source or test that demonstrates the behavior.
