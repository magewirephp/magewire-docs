# Upgrade

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/upgrading") }}

## Requirements

!!! warning "Alpine JS"
    AlpineJS must be removed from your instance before using Magewire. Since Magewire's JavaScript library already includes AlpineJS,
    having multiple instances can cause conflicts and unexpected issues.

- Magento version 2.4.4 or later
- PHP version 8.1 or later

## Breaking Changes

The first version of Magewire started as an experiment, with no clear direction or certainty about its future.
This meant that some assumptions were made—some of which turned out to be incorrect. These need to be corrected to stay
aligned with Livewire’s changes and to ensure that certain features, or those relying on specific concepts, function as intended. 

### Array Property Hooks

WIP...
