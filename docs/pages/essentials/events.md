# Events

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/components") }}

## Component Hooks

Magewire allows developers to register Component Hooks when creating new features.

These hooks are simple classes with a `provide` method that carry listeners for various events and can act as middleware.

### Creating a Component Hook
Component hooks provide a powerful way to intercept and modify the behavior of Magewire components at different stages of their lifecycle.

#### Basic Hook Structure

```php
<?php

class SupportExample extends \Magewirephp\Magewire\ComponentHook
{
    // Very useful when building a feature.
    public function provide(): void
    {
        \Magewirephp\Magewire\on('render', function (Component $component, AbstractBlock $block) {
            // Before rendering.
        
            return function (string $html) {
                return $html; // After rendering.
            };
        });
    }
}
?>
```

#### Hook Behavior

**Before:** When no callback is returned, the hook acts as a "before" plugin.

**After:** When returning a callback that accepts the returned arguments, it acts as an "after" plugin.

### Observer Events
For developers familiar with Magento's observer pattern, Magewire provides an alternative approach using regular Observer Events. This method is ideal when you don't need to create a full-featured component hook.

#### Event Configuration
Observer events work similarly to component hooks but use Magento's standard event system. A Data Transfer Object (DTO) is passed along, which allows you to register listener callbacks.

All Magewire events are prefixed with `magewire_on_` followed by the event name.

```xml title="etc/frontend/events.xml"
<event name="magewire_on_render">
    <observer name="MagewireOnRender"
              instance="Example\Module\Observer\Frontend\MagewireOnRender"
    />
</event>
```

Observer Implementation

```php
<?php

class MagewireOnRender implements \Magento\Framework\Event\ObserverInterface
{
    public function execute(\Magento\Framework\Event\Observer $observer): void
    {
        /** @var \Magewirephp\Magewire\Features\SupportMagentoObserverEvents\DTO\ListenerDataTransferObject $listener */
        $listen = $observer->getData('listener');

        $listen->with(function ($component, $block) {
            // Before rendering.
            
            return function (string $html) {
                return $html; // After rendering.
            };
        });
    }
}
?>
```

### Available Events

!!! info "Event Source"
    Most events are inherited from Livewire, with additional Magewire-specific events identifiable by the `magewire:` prefix.

#### Page Request

Events that occur during initial page loads:

- magewire:construct
- pre-mount
- mount
- magewire:precompile
- magewire:compiled
- render
- dehydrate
- checksum.generate
- destroy

#### Update Request

Events that occur during component updates (subsequent requests):

- checksum.verify
- checksum.generate
- snapshot.verified
- request
- magewire:reconstruct
- hydrate
- call
- magewire:precompile
- magewire:compiled
- render
- dehydrate
- checksum.generate
- destroy
- response

#### Lifecycle

Core component lifecycle events:

- magewire:construct
- magewire:precompile
- magewire:compiled
- magewire:reconstruct

- pre-mount
- mount.stub
- mount
- hydrate
- update
- call
- render
- render.placeholder
- dehydrate
- destroy

#### Request / Response cycle

- request
- response

#### Checksum operations

checksum.generate
checksum.verify
checksum.fail
snapshot-verified

#### Magic methods

- __get
- __unset
- __call

#### Utility events

- exception
- flush-state
- profile

!!! warning "Event Name Conversion"
    When using Magento Observer Events, special characters in event names are converted to underscores due to Magento's naming restrictions. For example, . becomes _ in the observer event name.
