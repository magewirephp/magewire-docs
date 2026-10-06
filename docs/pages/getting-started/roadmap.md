# Roadmap

Magewire's roadmap is intentionally conservative: tagged source describes what has shipped, while issues and pull requests describe work that may still change. This page does not promise delivery dates.

## Recently shipped

| Release | Capability |
|---|---|
| 3.2 | Theme integrations moved to standalone Composer packages. |
| 3.3 | Expression-aware directives, compiler cache command, compiler mechanism, pluggable multiple-root handling, and removal of experimental facades. |
| 3.3.1 | Parser, PHP reflection, and Magento 2.4.6 DI compilation fixes. |
| 3.4 | Lazy component loading. |
| 3.5 | Magento-backed application container and pre-reconstruction request filters. |
| 3.6 | Component-state pagination, temporary rate-limit lockouts, notifier coalescing, and a template-fragment compiler fix. |
| 3.6.1 | Canonical `magewireRuntime` and `magewireRuntimeBindings` Alpine providers. |
| 3.7 | Framework-independent core styles, the adaptive loading indicator, layout overrides for listeners, loaders, and modifiers, and service type sequences. |
| 3.7.1 | Notifier pinned to the bottom start edge on wide screens. |
| 3.7.2 | Security release for [GHSA-64j9-rg74-hqc7](https://github.com/magewirephp/magewire/security/advisories/GHSA-64j9-rg74-hqc7): only application actions are browser-callable. |

See [Feature History](releases/feature-history.md) for details and links to the relevant documentation.

## Current compatibility gaps

Magewire's ported tree contains upstream Livewire code that is deliberately not registered. These areas should be treated as potential future work, not available features:

- Livewire form objects and its full validation feature;
- file uploads;
- `Component::js()` browser evaluation;
- `wire:navigate` and Laravel-specific routing or session integrations.

Flakes remain experimental and are intentionally omitted from the public navigation until their implementation and API are stable.

## Follow development

Use the [Magewire issue tracker](https://github.com/magewirephp/magewire/issues), pull requests, and tagged releases for current plans. A proposal becomes supported behavior only after it lands in a release and its runtime integration is enabled.

Concrete use cases, reproducible failures, tests, and pull requests are the most useful ways to influence priorities. Security reports must follow the private process described on the documentation home page.
