# Patterns

<a id="magewire-object-on-init-event"></a>
<a id="alpinejs-function-proxy"></a>

The Alpine `Alpine.data()` proxy example previously published here has been retired. It depended on script execution
order and could silently miss or wrap an already-registered Alpine component.

Register Alpine components and extensions through a theme compatibility module at a defined Magewire layout container.
See [Layout containers](../theming/layout-containers.md), [Alpine loading](../theming/alpine-loading.md), and the
[JavaScript API](javascript/index.md) for supported extension points.
