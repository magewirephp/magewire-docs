# Lazy Loading

{{ include("admonition/magewire-specific.md", since_version="3.4.0") }}

Lazy components postpone mounting and rendering until the browser needs them. This is useful for expensive components below the fold or components that do not need to delay the initial page response.

## Enable lazy loading

Use the `Lazy` attribute when a component should always load lazily:

```php
<?php

namespace Vendor\Module\Magewire;

use Magewirephp\Magewire\Attributes\Lazy;
use Magewirephp\Magewire\Component;

#[Lazy]
class Recommendations extends Component
{
}
```

The default mode is `on-intersect`: Magewire loads the component when its placeholder enters the viewport.

Layout XML can opt in, or override the attribute, for a particular block:

```xml
<block name="recommendations" template="Vendor_Module::magewire/recommendations.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object">Vendor\Module\Magewire\Recommendations</argument>
        <argument name="magewire:component:lazy" xsi:type="string">on-load</argument>
    </arguments>
</block>
```

Accepted values are:

- `on-intersect` or `true`: load when the placeholder enters the viewport.
- `on-load`: load after the page initializes.
- `false`: disable lazy loading for this block, including when the class has `#[Lazy]`.

The layout value takes precedence over the component attribute.

## Placeholder

During the initial page render, Magewire skips the component's `mount()` method and normal template render. The component may provide a placeholder instead:

```php
public function placeholder(array $params = []): string
{
    return '<div class="skeleton" aria-busy="true">Loading…</div>';
}
```

The returned value can be one-root HTML or a Magento template identifier:

```php
public function placeholder(array $params = []): string
{
    return 'Vendor_Module::magewire/placeholder.phtml';
}
```

Without a custom placeholder, Magewire renders `<div></div>`. Keep a stable single root element so the loaded component can replace it cleanly.

## Isolation and bundling

Lazy components are isolated into separate requests by default. Disable isolation when several lazy components should join the same request:

```php
#[Lazy(isolate: false)]
class Recommendations extends Component
{
}
```

Component parameters are resolved again from Magento layout data when the lazy request runs; they are not trusted from browser-provided placeholder state.
