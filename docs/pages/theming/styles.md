# Core Styles

{{ include("admonition/magewire-specific.md", since_version="3.7.0") }}

Magewire ships a framework-independent stylesheet for the UI it renders itself: the notifier, the
[loading indicator](../features/loading-indicator.md), the exception placeholder, and the states of directives such as `wire:loading`. It needs no Tailwind
build or theme integration. Themes adjust it through CSS custom properties (tokens) or their own rules.

## How the stylesheet loads

The base layout adds the file to the page head:

```xml title="src/view/base/layout/default.xml"
<head>
    <css src="Magewirephp_Magewire::css/magewire.css"/>
</head>
```

It is a normal Magento static asset, so it is merged, minified, and deployed like the theme's own CSS. In production
mode, run `bin/magento setup:static-content:deploy` after upgrading.

Before 3.7.0, core only shipped the directive-state rules, rendered as an inline `<style>` block named `magewire.css`
in `head.additional`, and left the notifier and exception styling to Tailwind classes. That block no longer exists, so
layout instructions that reference it have no effect.

## What it styles

| Area | Selectors |
|---|---|
| Directive states | `[wire:loading]` and its modifiers, and `[wire:offline]`, are hidden until active. `[wire:dirty]` is hidden on elements other than `input`, `select`, and `textarea`. `[x-cloak]` is hidden. There is no `wire:cloak` rule. |
| Exception placeholder | `.magewire-exception`, `.magewire-exception-trace`, `.magewire-exception-label`, `.magewire-exception-message` |
| Utilities | `.magewire-sr-only`, `.magewire-loading-icon` with `-track` and `-indicator` parts, `.magewire-loading-indicator`, `.magewire-loading-indicator-spinner` |
| Notifier | `.magewire-notifier` and the classes listed under [Notifier markup](#notifier-markup) |

## Customize with tokens

Tokens come in two scopes, and the scope decides where an override must go.

### Notifier tokens declared on `.magewire-notifier`

The stylesheet declares these on the notifier element itself. A value set on `:root` is replaced by that declaration,
so override them on `.magewire-notifier`:

| Token | Default |
|---|---|
| `--magewire-notifier-gap` | `0.25rem`, and `0.5rem` from `48rem` |
| `--magewire-notifier-offset` | `0.5rem`, and `1rem` from `48rem` |
| `--magewire-notifier-width` | `26rem` (from `48rem`) |
| `--magewire-notifier-z-index` | `40` |
| `--magewire-notifier-surface` | `#fff` |
| `--magewire-notifier-border` | `#e8e8ec` |
| `--magewire-notifier-color` | `#1c2024` |
| `--magewire-notifier-muted-color` | `#60646c` |
| `--magewire-notifier-radius` | `0.75rem` |
| `--magewire-notifier-shadow` | `0 1px 2px rgb(15 23 42 / 6%), 0 8px 24px rgb(15 23 42 / 10%)` |
| `--magewire-notifier-padding-block` | `0.875rem` |
| `--magewire-notifier-padding-inline` | `1rem` |

```css
.magewire-notifier {
    --magewire-notifier-radius: 0.25rem;
    --magewire-notifier-surface: #111827;
    --magewire-notifier-border: #374151;
    --magewire-notifier-color: #f9fafb;
    --magewire-notifier-muted-color: #d1d5db;
}
```

The gap and offset are declared again inside `@media (min-width: 48rem)`. Override them inside the same media query
when you change them for wide screens.

### Tokens read with a fallback

Core reads these tokens with a built-in fallback but never declares them, so they can be set on `:root` or on any
ancestor of the element:

| Token | Default |
|---|---|
| `--magewire-notifier-{type}` | Accent color: border stripe and badge border |
| `--magewire-notifier-{type}-surface` | Badge background |
| `--magewire-notifier-{type}-color` | Badge text |
| `--magewire-notifier-enter-duration` | `400ms` |
| `--magewire-notifier-enter-easing` | `cubic-bezier(0.16, 1, 0.3, 1)` |
| `--magewire-notifier-leave-duration` | `150ms` |
| `--magewire-exception-border` | `#e8e8ec` |
| `--magewire-exception-accent` | `#f53003` |
| `--magewire-exception-radius` | `0.75rem` |
| `--magewire-exception-shadow` | `0 1px 2px rgb(15 23 42 / 6%)` |
| `--magewire-exception-surface` | `#fff` |
| `--magewire-exception-color` | `#1c2024` |
| `--magewire-loading-indicator-color` | `#6b7280` |

`{type}` is `neutral`, `success`, `info`, `warning`, or `error`. The `notice` type uses the `info` tokens, and any other
type uses `neutral`.

| Type | Accent | Surface | Color |
|---|---|---|---|
| `neutral` | `#64748b` | `#f8fafc` | `#334155` |
| `success` | `#16a34a` | `#f0fdf4` | `#166534` |
| `info` / `notice` | `#006aff` | `#eff6ff` | `#1d4ed8` |
| `warning` | `#d97706` | `#fffbeb` | `#92400e` |
| `error` | `#f53003` | `#fff1ed` | `#c42602` |

```css
:root {
    --magewire-notifier-success: #047857;
    --magewire-loading-indicator-color: #1d4ed8;
}
```

`--livewire-progress-bar-color` (`#2299dd`) is declared on `:root`. Override it on `:root` in a stylesheet that loads
later, or with a more specific selector such as `html:root`.

## Notifier markup

When you replace the notifier template, keep the classes and attributes the stylesheet targets:

| Element | Classes and attributes |
|---|---|
| Container | `magewire-notifier`, bound through `x-bind="magewireNotifierBindings"` |
| Notification | `message`, `magewire-notifier-item`, the type as a class, and `data-type="{type}"` |
| Occurrence badge | `magewire-notifier-occurrences`, shown from two occurrences, plus `magewire-notifier-occurrences--emphasized` above ten |
| Content | `magewire-notifier-before`, `magewire-notifier-body`, `magewire-notifier-title`, `magewire-notifier-message`, `magewire-notifier-after` |
| Close button | `magewire-notifier-close` and `magewire-notifier-close-icon` |
| Transitions | `magewire-notifier-transition-enter`, `-enter-start`, `-enter-end`, `-leave`, `-leave-start`, and `-leave-end`, applied through `x-transition` |

The close button is rendered by the `magewire.ui-components.notifier.close-button` block inside the
`notification.after` child of the notifier. Remove or replace that block to change it.

### Position

Below `48rem`, notifications stack at the bottom of the viewport, centered, at nearly full width. From `48rem`, the
stack is pinned to the bottom start edge with a width of `--magewire-notifier-width`. Start is the left edge in a
left-to-right page and the right edge in a right-to-left page. Magewire 3.7.0 centered the stack on wide screens;
3.7.1 moved it to the start edge so it does not cover centered primary actions.

To center it again, override the wide-screen rule with a selector that wins over `.magewire-notifier`:

```css
@media (min-width: 48rem) {
    html .magewire-notifier {
        inset-inline: 0;
        align-items: center;
        margin-inline: auto;
    }
}
```

### Motion

With `prefers-reduced-motion: reduce`, notifications fade without moving, and neither the emphasized badge nor the
loading icon animates.

## Remove the stylesheet

Prefer tokens and targeted overrides. If a theme supplies all of these styles itself, remove the asset in the theme's
layout:

```xml
<head>
    <remove src="Magewirephp_Magewire::css/magewire.css"/>
</head>
```

The theme then has to provide the directive-state rules as well. Without them, `wire:loading`, `wire:offline`, and
`wire:dirty` elements are visible before they should be, and `x-cloak` no longer hides content.

## Preview with the UI workbench

Open `/magewire/playwright/ui` on an installation in default or developer mode to inspect the styles without
reproducing application states. In production mode the route returns a 404 page.

The workbench renders the real notifier, loading icon, exception template, and Magewire directives. Its controls keep
every notification visible, let notifications expire, replay every message type, or clear the preview. The page loads
an extra stylesheet for its own layout, which does not apply anywhere else. A theme compatibility module can visit the
same route in its own Playwright suite to check its overrides against the core markup.

## Upgrading from Magewire 3.6

- The `magewire.css` block is gone. Use `<remove src="Magewirephp_Magewire::css/magewire.css"/>` to drop the
  stylesheet.
- The `magewire.ui-components.notifier.activity-state` and `…activity-state.loader-icon` blocks and the
  `activity-state.phtml` template were removed. Core no longer shows a spinner inside notifications. The
  `notification.loader.active` state is still maintained, so a theme can render its own indicator in
  `notification.after`.
- Notifications now have a close button.
- Core templates no longer contain Tailwind classes. Rules that targeted them must use the new classes:

    | Before | Since 3.7.0 |
    |---|---|
    | `relative` on the notification | `magewire-notifier-item` and `data-type` |
    | Position and color utilities on the badge | `magewire-notifier-occurrences` |
    | `animate-bounce` on the badge | `magewire-notifier-occurrences--emphasized` |
    | `sr-only` | `magewire-sr-only` |
    | `animate-spin`, `opacity-25`, `shadow-md` in the loading icon | `magewire-loading-icon`, `-track`, `-indicator` |
    | Utility classes in the exception placeholder | `magewire-exception-*` |
    | `x-transition:enter.duration.400ms` / `leave.duration.100ms` | `magewire-notifier-transition-*` classes |

- Core no longer adds itself to Hyvä's Tailwind build. Tailwind styling for Hyvä now lives in
  `magewirephp/magewire-hyva-theme`; see [Tailwind](tailwind.md).
- On wide screens the notifier now sits at the bottom start edge. See [Position](#position).

## Related

- [Magewire Notifier](../advanced/javascript/addons/magewire-notifier.md): the notifier's JavaScript API.
- [Layout](../advanced/architecture/layout.md): the blocks that render the notifier and loading indicator.
- [Build a compatibility module](compatibility-module.md): packaging theme overrides.
- [Exception handling](../advanced/exception-handling.md): when the exception placeholder is rendered.
