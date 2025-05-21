# Best Practices

## Modules Structure

When creating a module, we encourage you to follow a consistent directory and file structure to keep things organized
and familiar—similar to how View Models are typically placed in a `ViewModel` folder.

For modules, we tend to have the general rule to keep everything within the Magewire folder:

| Directory                    | Description                                                                                                                                                    |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **src/Magewire/--/-**        | All your components should be stored in a dedicated directory—either directly or organized within subdirectories—to keep the structure clean and maintainable. |
| **src/Magewire/Features/**   | Use a subdirectory named after your feature, starting with a capital letter.                                                                                   |
| **src/Magewire/Mechanisms/** | Use a subdirectory named after your mechanisms, starting with a capital letter.                                                                                |
