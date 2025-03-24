# Documentation

Magewire is heavily inspired by Livewire, and as a result, most of its core functionality works in the same way.
For this reason, all essential documentation can be found in the official [Livewire documentation](https://livewire.laravel.com/docs/quickstart).

The Magewire documentation primarily focuses on Magento-specific implementations, custom features,
and additional explanations that are either missing from the Livewire docs or are not relevant due to platform differences.

If you're looking for a deeper understanding of how Magewire works under the hood, we highly recommend referring to the
Livewire documentation alongside this guide.

## Structure

The Magewire documentation is intentionally structured in a way that closely follows the Livewire documentation.
This has been done to create a sense of familiarity, making navigation more intuitive and helping users better
understand how different concepts relate to each other. If you're already familiar with Livewire,
you should find it easy to adapt to Magewire.

To avoid unnecessary duplication, pages that exist in both the Magewire and Livewire documentation will always include
a direct link to the corresponding Livewire page for quick access. The Magewire documentation will only contain
additional information specific to Magewire, such as Magento-specific implementations, platform-specific limitations,
and custom features.

{{ include("admonition/livewire-reference.md", reference_url="#") }}

We deliberately avoid copying and pasting content from the Livewire documentation. Instead, our goal is to complement
it with details that are unique to Magewire, ensuring you get the most relevant and accurate information without redundancy.

## Clarity

We strive to keep this documentation as clean and clear as possible. This means that, in most cases, page titles will
consist of a single word rather than a full sentence. Titles are carefully chosen to be self-explanatory,
ensuring that readers can quickly understand the topic at a glance.

The goal is to make navigation intuitive and to avoid unnecessary complexity. By keeping titles concise,
it becomes easier to scan through the documentation and find the information you need without distractions.
If a topic requires further clarification, the content of the page itself will provide the necessary details.

## Contribute

If you notice any missing details or information in this documentation, please refer to the [Contribution](contribute.md) section.
We encourage everyone to contribute and help make the documentation as clear and accessible as possible for everyone.

## Includes

The following blocks are included as a preview of what to expect within these docs.

**Livewire Reference**
{{ include("admonition/livewire-reference.md", reference_url="#") }}

Magewire is heavily inspired by Livewire and, in many cases, works identically. As a result, rewriting the same
documentation would not only require a significant time investment but also create confusion when changes occur in either project.

Therefore, referring to the original Livewire documentation makes more sense.

However, this does not mean that everything in the Livewire documentation applies to Magento.
Some features are specific to Laravel, some may not make sense in the Magewire context, and others might be in
development.

**Magewire Experimental**
{{ include("admonition/magewire-experimental.md") }}

Magewire is an ambitious experiment with serious intentions. Some features should already be documented but require an
experimental flag to indicate that they are subject to change and should not be used in a production environment.

**Magewire Specific**
{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

For Magewire-specific features, we are introducing a "Magewire Specific" block. This serves as a clear indicator that
the content applies specifically to Magewire and also displays the version in which the feature was introduced.

While version-specific documentation with a version selector could be an option in the future,
we currently do not see an immediate need for it, and implementing it would be a significantly larger project.
