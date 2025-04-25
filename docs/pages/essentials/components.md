# Components

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/components") }}

## Creating components

Creating a basic Magewire component takes just a few minutes and requires only two or three files, depending on whether
you already have a layout handle. At its core, a Magewire component consists of two main files: a PHP class that handles
the logic and a template responsible for rendering the HTML on the frontend.

In the following example, we assume you are using layout XML to inject a Magewire component onto a page.
For more advanced use cases, we recommend exploring the in-depth documentation, where concepts like the
[resolver](../advanced/architecture/mechanisms/resolvers.md) mechanism will most likely play a role.

{{ include("create-a-component.md") }}
