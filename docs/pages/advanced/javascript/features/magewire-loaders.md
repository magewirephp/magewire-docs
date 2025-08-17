# Magewire Loaders

Magewire loaders have been a core feature since V1 and have been reintroduced and fully rewritten in V3. With the
much more advanced JavaScript layer behind Magewire, the options to do it the right way was one we could let go by.

## Class Properties

Loaders can be implemented in multiple ways. Using the protected `$loader` property allows you to display a notification
with a loading SVG (spinner by default) that appears only while the network processes the update request.

In the following example, a "**Processing...**" notification is shown to the user when an increment update request is being executed:

```php title="File: Magewire/Counter.php"
<?php

namespace Vendor\Module\Magewire;

class Counter extends \Magewirephp\Magewire\Component
{
    public int $count = 0;

    protected $loader = ['increment' => 'Processing...'];

    public function increment(): void
    {
        $this->count++;
    }
}
```

### Patterns

Since V3, the available options have increased, supporting different patterns such as
showing additional notifications when requests complete.

These are divided into two sections: **method calls** and **property update requests**.

#### Method Calls

| Pattern                                | Description                                               | Since |
|----------------------------------------|-----------------------------------------------------------|-------|
| `['{method}' => 'Loading']`            | Regular method call                                       | 1.0.0 |
| `['{method}' => 'Loading ... Loaded']` | Regular method call, followed by a processed notification | 3.0.0 |

!!! warning "WIP: more to follow soon"

#### Property Update Requests

| Pattern                                 | Description                              | Since |
|-----------------------------------------|------------------------------------------|-------|
| `['{property}' => 'Updating property']` | When a property update is behind handled | 3.0.0 |

!!! warning "WIP: more to follow soon"

### Hooks

Combining regular Magewire JavaScript hooks with the [Magewire Notifier addon](../addons/magewire-notifier.md) allows you to display custom messages.
However, this approach can be complex due to the variety of update types and method calls.

We want to demonstrate this capability as inspiration for alternative implementations when needed.

```html
<script>
    document.addEventListener('magewire:init', event => {
        const { addons, utilities } = event.detail.magewire;

        Magewire.hook('commit', ({ component, commit, respond, succeed, fail }) => {
            addons.notifier.create('Committed');

            succeed(({ snapshot, effect }) => addons.notifier.create('Succeeded'));
        });
    });
</script>
```
