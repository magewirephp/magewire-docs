# Upgrade Notes

These notes cover upgrades between Magewire V3 releases. Minor releases are backward compatible for documented APIs,
but they can change default presentation, layout structure, and companion package requirements. For a move from V1,
see [Upgrade](../upgrade.md).

## 3.7.1 to 3.7.2

!!! danger "Security release"
    3.7.2 fixes
    [GHSA-64j9-rg74-hqc7](https://github.com/magewirephp/magewire/security/advisories/GHSA-64j9-rg74-hqc7) (High),
    which affects Magewire 3.0.0 through 3.7.1. Upgrade every environment, including production, staging,
    development, local, demo, and test installations.

### Update the package

For a project whose root constraints already permit 3.7.2:

```shell
composer update magewirephp/magewire:3.7.2 --with-all-dependencies
composer show magewirephp/magewire
```

Review the lockfile, test the application, and deploy with your normal Magento process. If a root-level constraint
pins an older release, raise it, for example to `^3.7.2`. Coming from 3.6 or earlier, also apply
[3.6 to 3.7](#36-to-37).

The current companion packages accept 3.7.2 without a new release: `magewirephp/magewire-hyva-theme` 3.1.2
requires `>=3.7`, `magewirephp/magewire-hyva-checkout` 3.1.1 requires `~3.7.1`, and `magewirephp/magewire-admin`
3.0.0 requires `^3.0`.

### Inherited methods are no longer browser actions

Every public method defined on your component class is callable from the browser, even when no template refers to
it. That is unchanged. Before 3.7.2, the browser could also call public methods inherited from Magewire's
`Component` and `Component\Form` classes and their traits. These are now rejected with `MethodNotFoundException`,
for example:

- `reset`, `fill`, `only`, `except`, and `pull`;
- `redirect` and `skipRender`;
- `validate` and `validateOnly`;
- `tap` and accessors such as `getName`.

A method whose name starts with `__` is not callable, wherever it is declared. Magewire handles its own `__dispatch`
and `__lazyLoad` calls separately.

A template that calls one of these directly, such as `wire:click="reset"` or `$wire.reset()`, stops working. Add a
public action that checks the request and calls the helper:

```php
class CheckoutForm extends \Magewirephp\Magewire\Component\Form
{
    public string $email = '';

    public function clearEmail(): void
    {
        $this->reset('email');
    }
}
```

Then call `wire:click="clearEmail"`. Re-declaring an inherited method, such as `public function reset(...$properties)`,
makes it browser-callable again, so only do that deliberately.

Public methods on your own base classes and traits stay callable unless their name is reserved.

### Event listener targets are checked

A listener that points at a method inherited from `Component` or `Component\Form`, such as `reset`, or at a lifecycle
hook, such as `mount` or `boot`, now throws `MethodNotFoundException` when its event is dispatched. This applies to
`$listeners`, `#[On]`, and the [`magewire:listeners`](../../features/layout-overrides.md#listeners) layout argument.
Point the listener at a public action instead. A listener whose method is not declared on the component, and
`$refresh`, still re-render without calling anything.

### Reserved method names

These names belong to the framework. The browser cannot call them, and they cannot be listener targets:

- `boot`, `booted`, `mount`, `exception`, `rendering`, `rendered`, and `placeholder`;
- any name starting with `hydrate`, `dehydrate`, `updating`, or `updated`;
- a trait hook name: one of `boot`, `initialize`, `mount`, `hydrate`, `updating`, `updated`, `rendering`,
  `rendered`, `dehydrate`, `exception`, `call`, or `booted`, followed by the basename of a trait the component uses,
  such as `callRequest` or `initializeView`.

Names are matched case-sensitively, so declare lifecycle hooks in the casing shown. Rename an application action that
collides with one of these names, for example a public `placeholder()` action on a non-lazy component.

### Lazy loading

The internal `__lazyLoad` call is only accepted while a [lazy](../../features/lazy-loading.md) placeholder loads its
component. Lazy components need no change.

### What to check

- Search templates and scripts for `wire:` directives and `$wire` calls that name an inherited helper.
- Check every `$listeners` entry, `#[On]` method, and `magewire:listeners` item for an inherited helper or a reserved
  name.
- Check that public actions do not use a reserved name.

See Magewire's
[compatibility guide](https://github.com/magewirephp/magewire/blob/3.7.2/UPGRADING.md#browser-callable-component-methods)
and [Security](../../advanced/security.md#browser-callable-methods).

## 3.6 to 3.7

### Update the packages together

| Package | Release for Magewire 3.7 |
|---|---|
| `magewirephp/magewire` | 3.7.2 (security release) |
| `magewirephp/magewire-hyva-theme` | 3.1.2 (requires `>=3.7`) |
| `magewirephp/magewire-hyva-checkout` | 3.1.1 (requires `~3.7.1`) |

The Hyvä Checkout package accepts any Hyvä theme package version, so require the theme package explicitly. See
[Companion package compatibility](../versioning.md#companion-package-compatibility).

```shell
composer require magewirephp/magewire:^3.7.2 magewirephp/magewire-hyva-theme:^3.1.2
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
