# Upgrade Notes

These notes cover upgrades between Magewire V3 releases. Minor releases are backward compatible for documented APIs,
but they can change default presentation, layout structure, and companion package requirements. For a move from V1,
see [Upgrade](../upgrade.md).

## 3.6 to 3.7

### Update the packages together

| Package | Release for Magewire 3.7 |
|---|---|
| `magewirephp/magewire` | 3.7.1 |
| `magewirephp/magewire-hyva-theme` | 3.1.2 (requires `>=3.7`) |
| `magewirephp/magewire-hyva-checkout` | 3.1.1 (requires `~3.7.1`) |

The Hyvä Checkout package accepts any Hyvä theme package version, so require the theme package explicitly. See
[Companion package compatibility](../versioning.md#companion-package-compatibility).

```shell
composer require magewirephp/magewire:^3.7.1 magewirephp/magewire-hyva-theme:^3.1.2
bin/magento setup:upgrade
```

In production mode, also compile DI and deploy static content, which now includes Magewire's stylesheet.

### Core styles

- The inline `magewire.css` block is replaced by the `Magewirephp_Magewire::css/magewire.css` head asset. Layout
  instructions that reference the old block have no effect.
- Core templates no longer contain Tailwind classes. Theme CSS that targeted `relative`, `animate-bounce`, `sr-only`,
  `animate-spin`, or the old exception utilities must use the new `magewire-*` classes.
- The notifier's `activity-state` blocks were removed and a close button was added. Core no longer draws a spinner
  inside notifications.
- On wide screens, the notifier sits at the bottom start edge (3.7.1).

See [Core styles](../../theming/styles.md#upgrading-from-magewire-36) for the class mapping and tokens.

### Hyvä

- Run `bin/magento setup:upgrade` so Hyvä regenerates `app/etc/hyva-themes.json` without the core entry, then rebuild
  the theme with `npm run build`.
- Move overrides of the package's `--offset`, `--index`, and `--gap` properties to the core
  `--magewire-notifier-offset`, `--magewire-notifier-z-index`, and `--magewire-notifier-gap` tokens.

See [Tailwind](../../theming/tailwind.md#upgrading-from-package-311).

### Hyvä Checkout

- Since `magewirephp/magewire-hyva-checkout` 3.1.0, components without an attribute receive backwards compatibility
  when they render inside `hyva-checkout-main`. Add `#[HandleBackwardsCompatibility(enabled: false)]` to V3-native
  checkout components. See [Hyvä Checkout BC](../../theming/hyva-checkout-bc.md).
- Consecutive identical checkout flash messages are grouped with a count badge by default. Rebuild the Hyvä theme so
  the badge is styled, or turn the grouping off. See
  [Hyvä Checkout flash messages](../../theming/index.md#hyva-checkout-flash-messages).

### Loading indicator

Components that handle dispatched events now show a spinner when a request is slow. Review it on pages with event
listeners, and adjust or remove it as described in [Loading Indicator](../../features/loading-indicator.md).

### Service type sequences

`sequence` entries on Features, Mechanisms, and Containers are now enforced by item name. An existing entry can
reorder items, and setup fails with a `LogicException` on a cycle or when a `PERSISTENT` or `ALWAYS` item sequences
after a `LAZY` one. See [Ordering items](../../advanced/architecture/runtime.md#ordering-items).

### Behavior fixes to check

- A loader message that starts with `...`, such as `... Saved`, now shows nothing during the request instead of a
  "Message Unknown" notification.
- Dispatching an event that a component does not listen to now fails with `EventHandlerDoesNotExist` instead of a
  class-not-found error.

### New, optional

- [Layout overrides](../../features/layout-overrides.md): adjust listeners, loader messages, and component setup per
  layout block.
- The [UI workbench](../../theming/styles.md#preview-with-the-ui-workbench) at `/magewire/playwright/ui` renders the core
  UI outside production mode for styling work.

## 3.6.0 to 3.6.1

The Alpine runtime providers were renamed to `magewireRuntime` and `magewireRuntimeBindings`. The previous names still
work as deprecated aliases; update custom templates that reference them. See
[CSP Script Bootstrap](../../theming/csp-script-bootstrap.md#runtime-provider-names).
