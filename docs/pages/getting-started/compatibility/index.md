# Compatibility

It's a misconception that Magewire is compatible with all themes out of the box. While Magewire is primarily a backend framework,
it also includes several frontend elements. This means that certain backend events need to be translated to the frontend to function correctly.

For example, consider flash messages: Magewire allows you to dispatch a flash message from the PHP component,
and it automatically includes an event in the response containing all relevant details.

However, actually displaying the flash message on the frontend requires theme-specific implementation.
Ensuring that these events are properly handled in the frontend is what defines theme compatibility.

## Architecture

The `magewirephp/magewire` core module includes several submodules, with theme compatibility modules located under the `/themes` root directory.
Each of these is defined as a separate Magento module, and their names always follow the convention `MagewireCompatibilityWith[ThemeName]`.

For example, compatibility with Hyvä is provided by the `Magewirephp_MagewireCompatibilityWithHyva` module.

If the Hyvä team chooses to maintain their own compatibility module, it would typically be named `Hyva_MagewireCompatibilityWithHyva`,
indicating that the module is managed externally and therefore would not reside in the `/themes` folder.
