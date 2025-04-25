# Facades (experimental)

{{ include("admonition/magewire-experimental.md") }}

**Feature and Mechanism facades are currently experimental and may not be included in the final release.
While they aim to simplify development, they can also introduce complexity for those unfamiliar with the concept.
Magewire is designed to align closely with Magento’s core principles, though some necessary deviations have been made.
Facades, however, are not essential but rather a convenience feature. We welcome feedback on this approach,
which is why we have provided some documentation to facilitate discussion.**

## Understanding Facades
Facades in PHP provide a simple interface to complex class structures. In Magewire, they serve as entry points to features and mechanisms.

## Why Use Facades?
Magento development often involves interacting with multiple services, which can lead to tightly coupled, verbose code.
Facades streamline this by offering a clear, expressive API that abstracts away complexity, ensuring better maintainability and flexibility.

## Some Key Benefits
- **Simplifies Complex Systems** – Encapsulates intricate logic, allowing developers to focus on business requirements rather than low-level details.
- **Enhances Code Readability** – Provides well-named methods that make the API easier to understand and use.
- **Promotes Loose Coupling** – Shields client code from underlying changes, making the system more adaptable to future modifications.

## Development Best Practices
Not every feature or mechanism requires a facade; their implementation is at the developer’s discretion.

Facades are structured within their respective feature or mechanism subdirectories, maintaining clarity and consistency.
This organization ensures that developers can efficiently integrate Magewire’s capabilities into their Magento projects.

## Using a Facade
When your feature becomes big or you want to provide a simple entry to a reusable piece of code, you may decide to
implement a facade for your feature or mechanism. This is done via `di.xml`, where you inject your feature or mechanism
into the service provider. By using the `facade` item key, you can assign a facade class, making it accessible.

```xml
<item name="example_feature_name" xsi:type="array">
    <item name="type" xsi:type="string">
        ...
    </item>
    
    <item name="facade" xsi:type="string">
        Vendor\Module\Features\ExampleFeature\ExampleFeatureFacade
    </item>
</item>
```

```php
<?php

class Foo
{
    public function bar()
    {
        // A magic getter method on the Magewire Service Provider
        // lets you access the example feature facade.
        
        $exampleFeatureFacade = $this->magewireServiceProvider
            ->getExampleFeatureFacade();
    }
}
```
