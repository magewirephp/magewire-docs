# Facades

Magewire's experimental Feature and Mechanism facade API was removed in version 3.3. Existing facade examples are not compatible with current Magewire 3 releases.

Use the narrowest supported alternative:

- constructor injection and Magento `di.xml` for application services;
- the [Application Container](../application-container.md) when ported or runtime extension code needs `app()`-style resolution;
- `Magewirephp\Magewire\Features` or `Magewirephp\Magewire\Mechanisms` when framework extension code needs a registered service item;
- component hooks and observer events for lifecycle integration.

Do not add a `facade` key to feature or mechanism registration. Current service items accept their type, sort order, boot mode, and mechanism-specific view-model metadata; a facade is no longer constructed or exposed by the service provider.

This page remains as a migration marker so older links explain where the API went.
