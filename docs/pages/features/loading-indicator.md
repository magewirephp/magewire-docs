# Loading Indicator

{{ include("admonition/magewire-specific.md", since_version="3.7.0") }}

The loading indicator places a spinner over a component while one of its requests is slow. It works without any
template changes and is enabled by default after upgrading. It is separate from
[`wire:loading`](../html-directives/wire-loading.md), which you place on elements yourself, and from
[Magewire loaders](../advanced/javascript/features/magewire-loaders.md), which show notifier messages from a `$loader`
map.

## When it appears

By default, the indicator only covers components that update because they handle a dispatched event. A request
counts when one of its calls is Magewire's internal `__dispatch` call, which is what a component's
[event listener](../essentials/events.md) produces. The component the customer clicked or typed into is left to its own
`wire:loading` states.

Enable **Show Spinner on Interacted Components** to let every request count, including the component the customer
interacted with:

```text
Stores → Configuration → Advanced → Magewire → Features → Loading Indicator
```

| Setting | Config path | Default |
|---|---|---|
| Show Spinner on Interacted Components | `magewire/features/loading_indicator/show_interacted` | No |

The field is available per website and store view. With it enabled, polls, lazy loads, and updates started from
JavaScript count as well. The value is written into the page, so clean the `config`, `block_html`, and `full_page`
caches after changing it.

## Adaptive delay

The spinner appears only when a request is still running after a threshold. The threshold adapts to the component's
recent response times and to the connection:

| Condition | Threshold |
|---|---|
| Slow connection: `effectiveType` of `slow-2g` or `2g`, a round-trip time of 600 ms or more, or a downlink below 1 Mbps | 250 ms |
| Fewer than two recorded requests for the component | 500 ms |
| Median of the recorded requests is 600 ms or more | 250 ms |
| Median is 250 ms or less | 700 ms |
| Any other median | 500 ms |

The connection check uses the Network Information API where the browser supports it. Magewire records the duration
of every request per component name, keeps the last five, and stores them in `sessionStorage` under
`magewire:loading-indicator:timings`. When storage is not available, the samples are kept in memory for the page. A
component that is usually slow therefore shows the spinner sooner, and one that is usually fast rarely shows it.

These timings are browser-local heuristics, separate from the per-action timings used by
[Magewire loaders](../advanced/javascript/features/magewire-loaders.md#fast-request-suppression).

## Rendering and accessibility

When the spinner is shown, Magewire appends an overlay as the last child of the component's root element:

```html
<div class="magewire-loading-indicator" role="status" aria-label="Loading">
    <span class="magewire-loading-indicator-spinner" aria-hidden="true">
        <!-- magewire.ui-components.loading-indicator.spinner -->
    </span>
</div>
```

- The component root receives `aria-busy="true"`, and its previous value is restored afterwards.
- A root with `position: static` temporarily receives `position: relative` so the overlay can cover it.
- The overlay is transparent and uses `pointer-events: none`, so it does not block interaction.
- The overlay is re-attached after the component morphs.
- With `prefers-reduced-motion: reduce`, the spinner does not rotate.

The `aria-label` is translatable through the `Loading` phrase.

## Customize

Change the spinner color with a token, which can be set on `:root` or on a component:

```css
:root {
    --magewire-loading-indicator-color: #1d4ed8;
}
```

Replace the spinner icon:

```xml
<referenceBlock name="magewire.ui-components.loading-indicator.spinner"
                template="Vendor_Theme::magewire/loading-spinner.phtml"/>
```

The overlay and spinner classes, `.magewire-loading-indicator` and `.magewire-loading-indicator-spinner`, are part of
the [core styles](../theming/styles.md).

## Disable the indicator

There is no configuration switch that turns the indicator off. Remove its layout blocks in a theme or module layout
file:

```xml title="view/frontend/layout/default.xml"
<referenceBlock name="magewire.ui-components.loading-indicator" remove="true"/>
<referenceBlock name="magewire.addons.loading-indicator" remove="true"/>
<referenceBlock name="magewire.utilities.loading-indicator-timing" remove="true"/>
```

Remove all three. The UI subscribes to `window.MagewireAddons.loadingIndicator`, and the addon reads its thresholds
from `window.MagewireUtilities.loadingIndicatorTiming`. Removing the addon but keeping the UI block, or removing the
timing utility but keeping the addon, causes browser errors.

There is no per-component opt-out.

## JavaScript API

The addon is registered as `window.MagewireAddons.loadingIndicator`:

| Method | Result |
|---|---|
| `subscribe(listener)` | Call `listener(entry)` whenever an entry is shown or hidden. Returns an unsubscribe function. |
| `get(id)` | Return the entry for a component ID, or `null`. |
| `start(component, eligible = true)` | Track a request and return a `finish()` function. Only eligible requests can show the spinner, but every request is recorded. |
| `schedule(entry)` | Re-evaluate when an entry should become visible. |
| `cancel(id)` | Stop tracking a component and hide its spinner. |

An entry has the shape `{ id, component, requests, visible, timer }`. The addon hooks into Magewire's `commit` hook
itself; call `start()` only to track work that does not go through a Magewire commit.

The timing utility is registered as `window.MagewireUtilities.loadingIndicatorTiming`:

| Method | Result |
|---|---|
| `samples(name)` | Recorded durations for a component name. |
| `record(name, duration)` | Add a duration in milliseconds. |
| `threshold(name)` | The current threshold in milliseconds. |
| `shouldShow(name, elapsed)` | Whether `elapsed` has reached the threshold. |

## Related

- [`wire:loading`](../html-directives/wire-loading.md): element-level loading states.
- [Magewire loaders](../advanced/javascript/features/magewire-loaders.md): notifier messages during requests.
- [Core styles](../theming/styles.md): the overlay classes and tokens.
- [Layout](../advanced/architecture/layout.md): where the loading-indicator blocks live.
