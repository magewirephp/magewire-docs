# Layout

Magewire is a large framework with many options and features. Still, we aim to keep things as flexible as possible,
providing an easy way to inject additional JavaScript, UI components, and other frontend-related elements that Magewire needs.

It's impossible to explain everything, and many parts are self-explanatory or include clear comments in the layout files to indicate their purpose.

That said, we do want to document the most important containers and blocks to make things even clearer for those looking
for specific situations or guidance on where to place blocks.

## Containers

Magewire provides a carefully structured layout to keep things organized and clear. It includes dedicated containers for
everything related to Magewire, such as storing AlpineJS components, injecting custom feature-specific JavaScript,
or adding custom directives.

| Container                    | Description                                                                                                                                    |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| magewire.before              | A container intended for containers and blocks that should precede all Magewire-related containers and blocks.                                 |
| magewire.before.internal     | **Magewire-only:** A container intended for Magewire-specific logic that must be loaded before any internal Magewire elements are initialized. |
| magewire.internal            | **Magewire-only:** Intended for non-overridable internal code.                                                                                 |
| magewire.after.internal      | **Magewire-only:** A container intended for Magewire-specific logic that must be loaded after any internal Magewire elements are initialized.  |
| magewire.after               | A container intended for containers and blocks that should follow all Magewire-related containers and blocks.                                  |
| magewire.alpinejs.before     | Designed to hold custom AlpineJS code that must execute before any Magewire-specific AlpineJS logic.                                           |
| magewire.alpinejs.after      | Intended to hold custom AlpineJS code that must render after any Magewire-related AlpineJS code.                                               |
| magewire.alpinejs.components | Holds AlpineJS components that are specific to Magewire functionality.                                                                         |
| magewire.alpinejs.directives | Intended to hold custom AlpineJS directives.                                                                                                   |
| magewire.ui-components       | Intended to hold custom AlpineJS UI-components.                                                                                                |
| magewire.addons              | Intended to hold Magewire addons.                                                                                                              |
| magewire.directives          | Intended to hold Magewire directives.                                                                                                          |
| magewire.features            | Intended to hold Magewire feature code.                                                                                                        |
| magewire.features            | Intended to hold Magewire feature code.                                                                                                        |
| magewire.disabled            | A container for rendering specific elements only when Magewire is not active on the page.                                                      |
| magewire.disabled            | A container for rendering specific elements only when Magewire is not active on the page.                                                      |
