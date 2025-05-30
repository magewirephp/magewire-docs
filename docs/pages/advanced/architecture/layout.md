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

| Container                    | Description                                                                                                               |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| magewire.before              | Container for elements that should precede all Magewire-related containers and blocks                                     |
| magewire.before.internal     | **Magewire-only:** Container for Magewire-specific logic that must load before internal Magewire elements are initialized |
| magewire.internal            | **Magewire-only:** Contains non-overridable internal code                                                                 |
| magewire.after.internal      | **Magewire-only:** Container for Magewire-specific logic that must load after internal Magewire elements are initialized  |
| magewire.after               | Container for elements that should follow all Magewire-related containers and blocks                                      |
| magewire.alpinejs.before     | Contains custom AlpineJS code that must execute before Magewire-specific AlpineJS logic                                   |
| magewire.alpinejs.after      | Contains custom AlpineJS code that must render after Magewire-related AlpineJS code                                       |
| magewire.alpinejs.components | Contains AlpineJS components specific to Magewire functionality                                                           |
| magewire.alpinejs.directives | Contains custom AlpineJS directives                                                                                       |
| magewire.ui-components       | Contains custom AlpineJS UI components                                                                                    |
| magewire.utilities           | Contains Magewire utilities                                                                                               |
| magewire.addons              | Contains Magewire addons                                                                                                  |
| magewire.directives          | Contains Magewire directives                                                                                              |
| magewire.features            | Contains Magewire features                                                                                                |
| magewire.disabled            | Container for rendering elements only when Magewire is not active on the page                                             |

## Directories & Templates

Magewire got a complete overhaul of its folder structure that has been well thought through in terms of simplicity
and structuring things in a loosely coupled way.

### Basics

When you look in the core module `src/view/base` area templates directory, you'll find two folders: `js` and `magewire`.
The first holds only templates with primarily `<script>` elements including mainly JavaScript, ordered in subdirectories
according to their targeted library. So for example, everything Alpine related, even if it is for Magewire,
should go into the `alpinejs` directory.

One exception is that there can sometimes be files that don't have any JavaScript content in them,
but are empowering child blocks by, for instance, making sure they are rendered.

One example of this can be found at:
`src/view/base/templates/js/alpinejs/component/magewire-notifier.phtml`.

### Directories

| Directory                   | Description                                                                                          |
|-----------------------------|------------------------------------------------------------------------------------------------------|
| js/**/*`                    | Contains templates with primarily JavaScript content                                                 |
| js/alpinejs/**/*            | Contains templates with AlpineJS-related JavaScript                                                  |
| js/alpinejs/components/**/* | Contains AlpineJS components only                                                                    |
| js/alpinejs/directives/**/* | Contains AlpineJS directives only                                                                    |
| js/magewire/**/*            | Contains templates with Magewire-related JavaScript                                                  |
| js/magewire/utils/**/*      | Contains Magewire utilities only                                                                     |
| js/magewire/addons/**/*     | Contains Magewire addons only                                                                        |
| js/magewire/directives/**/* | Contains Magewire directives only                                                                    |
| js/magewire/features/**/*   | Contains JavaScript for Magewire Feature support, always divided with a lower-kebab-cased subfolder. |

!!! tip "Building something custom or making a contribution? Always examine the folder and file structure closely to ensure you're in the right location."
