# Documentation

{{ include("admonition/documentation-under-construction.md") }}

Magewire is heavily inspired by Livewire, and as a result, most of its core functionality works in the same way.
For this reason, all essential documentation can be found in the official [Livewire documentation](https://livewire.laravel.com/docs/quickstart).

The Magewire documentation primarily focuses on Magento-specific implementations, custom features,
and additional explanations that are either missing from the Livewire docs or are not relevant due to platform differences.

If you're looking for a deeper understanding of how Magewire works under the hood, we highly recommend referring to the
Livewire documentation alongside this guide.

## Disclaimer

These docs are written based on the knowledge and experience we had at the time of writing.

If you notice anything incorrect, unclear, in need of expansion, or outdated, feel free to open a pull request.
We’ll review it as soon as possible.

## Tone of Voice

The tone of voice should always be professional, clear, and inclusive. We write from a "we" perspective
rather than an "I" perspective to reflect a collaborative effort.

Since these docs are primarily aimed at developers, we use a direct and instructional tone when providing step-by-step guidance.
Addressing the reader with "you" ensures clarity and engagement.

**Key Principles:**

- Clarity & Precision – Avoid ambiguity and unnecessary complexity. Be concise but thorough.
- Consistency – Use a uniform tone and terminology throughout the documentation.
- Respect & Inclusivity – We respect and welcome everyone. Our language should be neutral, inclusive, and non-discriminatory.
- Empathy – If something is unclear or if our tone ever feels unwelcoming, we encourage feedback. Please let us know, and we will work to improve it.
- Encouraging & Helpful – When explaining concepts, especially for beginners, be supportive and assume good intent.

By following these guidelines, we aim to create documentation that is helpful, approachable, and professional for all developers.

## Navigation

The navigation structure has been mirrored from the Livewire 3 documentation, with a few additions.
The goal is to keep things in sync, making content easier to navigate and understand.

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

**Livewire Concept**

{{ include('admonition/livewire-concept.md') }}

To indicate that the explanation pertains to Livewire.

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

## AI

Writing good documentation is a skill in itself. An explanation can be technically accurate but may not always be clear, concise, or well-structured in terms of vocabulary and readability. To enhance the quality of our documentation, we use AI as an assistant, but with clear boundaries.

**Writing Guidelines:**

- AI as a Writing Aid, Not a Replacement – AI helps refine wording, improve clarity, and enhance readability. However, it does not replace human judgment or expertise.
- Human Oversight is Essential – Every AI-generated suggestion must be reviewed and approved by a human to ensure it aligns with our documentation standards and intent.
- No AI-Generated Code – AI should not be used to write the initial code examples. Code should be written by developers first, ensuring correctness, best practices, and relevance. AI may assist in refining or improving existing code, but all changes must be carefully reviewed by a developer.
- Maintain Consistency – AI should be used to align tone and structure but must follow the established style and technical accuracy of the documentation.

By using AI thoughtfully and responsibly, we ensure that our documentation remains human-centered, high-quality, and reliable while benefiting from AI-driven enhancements.

!!! info "Future Considerations: Automated Tone of Voice Checks"
    We are exploring the possibility of implementing a GitHub action workflow that periodically reviews all Markdown
    files within the pages folder. The goal is to ensure a consistent tone of voice throughout the entire documentation.

    While this is not a priority at the moment, it remains a potential future improvement to maintain quality
    and uniformity in our documentation.

This prompt can be used when requesting AI to refine and enhance a specific section of your writing.

```text
WIP...
```
