# Basics

A Magewire component combines a PHP class with a `.phtml` template. Magento layout XML places the component on a page;
Magewire then keeps its public state and the rendered DOM synchronized across update requests.

Before continuing, install and enable Magewire as described on the [documentation home page](../../index.md).

## Build a counter

The following example creates a complete component, binds it to a Magento block, and calls a PHP action from the
browser.

{{ include("create-a-component.md") }}

## The request cycle

The counter demonstrates Magewire's normal request cycle:

1. Magento renders the layout block and component template.
2. Magewire serializes the component's public state into a signed snapshot.
3. `wire:click="increment"` sends that snapshot and the requested action to the Magewire update route.
4. Magewire reconstructs the component, calls `increment()`, and renders the template again.
5. The browser processes the response and morphs only the changed DOM.

Component snapshots are browser-visible data. Never put secrets in public properties, and always authorize sensitive
actions on the server.

## Passing initial values from layout XML

Use a `magewire.` argument for a public property and a `magewire:mount:` argument for a named `mount()` parameter:

```xml
<argument name="magewire.label" xsi:type="string">Items</argument>
<argument name="magewire:mount:start" xsi:type="number">19</argument>
```

```php
public string $label = 'Counter';

public function mount(int $start = 0): void
{
    $this->count = $start;
}
```

The layout resolver converts kebab-case argument names to camelCase. For example,
`magewire:mount:page-size` is passed as `$pageSize`.

See [Components](../essentials/components.md) for every supported binding shape and argument group. Continue with
[Properties](../essentials/properties.md), [Actions](../essentials/actions.md), and the
[HTML directives](../html-directives/wire-click.md) when you are ready to add real behavior.
