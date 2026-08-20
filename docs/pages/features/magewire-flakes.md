# Flakes

{{ include("admonition/magewire-experimental.md") }}

Flakes are present in the Magewire 3 source as an experimental compiler and resolver concept, but they are not a stable public API in the current release.

The current implementation expects `<flake:{variant}>` compiler tags; older examples using `<magewire:message>` are obsolete. Magewire 3.5 also registers a `FlakeFragment` class name that is not present at that path, so a clean installation cannot be documented as a dependable end-to-end workflow yet.

For production code:

- use nested Magewire components when a child needs independent state and requests;
- use ordinary Magento child blocks when markup can remain part of the parent's render;
- use custom [fragment types](../concepts/fragments.md#custom-fragment-types) for output post-processing without a child component.

This page is intentionally omitted from navigation until the source registration, syntax, tests, and supported nesting behavior agree.
