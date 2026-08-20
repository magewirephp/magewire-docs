# wire:current

{{ include("admonition/magewire-unsupported.md") }}

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/wire-current") }}

The Magewire browser bundle contains the upstream directive, but Magewire does not currently promise Livewire's
SPA-navigation lifecycle. Magento normally performs full-page navigation and has its own route, menu, and breadcrumb
state, so `wire:current` is not part of Magewire's supported directive surface.

Render active classes and `aria-current="page"` from Magento route or navigation state instead. If a component changes
an active item without navigation, use a component property with [`wire:show`](wire-show.md) or an Alpine class binding.

Treat any apparent `wire:current` behavior in Magewire 3.5 as an implementation detail until navigation support is
documented explicitly.
