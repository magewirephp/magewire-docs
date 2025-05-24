# Feature History

This list found below provides an overview of newly introduced features across different versions.
Each version listed includes a bullet-point summary of what has been added, ensuring a quick and clear understanding
of new capabilities.

Versions not included in this log indicate releases where no new features were introduced.

## 3.0.0-beta1

- **Dedicated Documentation**

  Unlike V1, Magewire V3 now features its own dedicated, GitHub-hosted documentation, powered by MkDocs.

  By moving the documentation out of the core repository and into a centralized location, we aim to provide a more
  structured and accessible knowledge base.

  This dedicated space makes it easier to find answers, stay up to date, and get inspired—ultimately helping developers build better,
  more powerful features with Magewire.

- **Template @ Directives**
  
  Using template `@` directives allows developers to write simplified syntax that is transformed into more complex PHP code during template compilation.
  Templates are automatically recompiled whenever a `.phtml` file is modified, ensuring changes are always up to date.

- **Template Fragments**

  Provides the ability to mark a specific area within a template, allowing modifiers to alter its content—such as
  making inline scripts CSP compliant. This is done using the `$fragment = $viewModel->utils()->template()->fragment()` chain,
  followed by `$script = $fragment->script()->start()` and `$script->end()` to define the fragment boundaries.

  For more details, please refer to the [Fragments](../../concepts/fragments.md) documentation.

- **Automatic View Model Resolving**

  Blocks that are direct or indirect children of the magewire block will automatically receive a `view_model` argument—as
  long as it hasn’t already been manually defined. This reduces the need to explicitly bind the `view_model` to each individual block,
  resulting in cleaner and more maintainable layout XML.

  For more details, please refer to the [Notables](../../getting-started/notables.md#the-magewire-block) documentation.

- **Portman**

  A tool that enables developers to port packages from other communities into Magento, making it possible to reuse a
  wide range of existing code and reduce duplication across ecosystems.

  For more details, please refer to the [Portman](../../advanced/architecture/portman.md) documentation.

- **CSP Complaint**

  Since April 2025, it is recommended that all payment-related functionality is CSP compliant—meaning that any scripts,
  styles, or other resources involved in the payment process must adhere to Content Security Policy standards.

  This includes using `nonces` or `hashes` for inline scripts and ensuring that all external resources are loaded from trusted,
  whitelisted domains. Doing so enhances the security of the checkout process and helps prevent cross-site scripting (XSS) attacks.

- **Components Hooks**

  Compared to V1, Magewire V3 introduces a wide range of new extension points throughout the backend architecture.
  Developers can now hook into various stages of the component lifecycle—including rendering, hydration, dehydration,
  and more—making it easier to customize and extend Magewire's behavior in powerful and flexible ways.

- **View Model Utilities**

  The primary Magewire ViewModel has been extended with a `utils` API, giving developers easy access to commonly used
  tools—both within and outside Magewire component template files. This eliminates the need to repeatedly create custom
  ViewModels for basic functionality.

  The `utils` API is designed to be extensible, allowing you to add custom utilities when needed.
  However, in most cases, it should already provide everything you need out of the box.
