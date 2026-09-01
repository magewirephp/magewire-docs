# Hyvä CSP Script Bootstrap

Magewire provides Alpine.js on pages containing Magewire components. The
`magewirephp/magewire-hyva-theme` compatibility package loads that bundle without
also loading Hyvä's standalone Alpine.js bundle. Pages without Magewire
components continue to use Hyvä's Alpine runtime.

The Magewire script needs runtime request configuration, including the update
URI and the current Magento form key. Following Livewire's DOM contract, those
values must ultimately exist as `data-update-uri` and `data-csrf` attributes on
the script element.

## Why the script cannot be the Alpine component

Alpine's CSP build deliberately prohibits evaluating expressions on a `script`
element. Consequently, this markup is not CSP compatible:

```html
<script
    id="magewire-script"
    src="magewire.csp.min.js"
    x-data="magewireRuntime"
    x-bind="magewireRuntimeBindings"
></script>
```

During `Alpine.start()`, the CSP evaluator encounters `x-data` on an
`HTMLScriptElement` and throws before Livewire can finish initializing. Events
such as `livewire:initialized` and the corresponding Magewire compatibility
events are then never dispatched.

CSP does not prohibit normal attributes such as `src`, `data-csrf`, or
`data-update-uri` on a script. Only the Alpine directives need another host.

## Bootstrap structure

The Hyvä compatibility package separates Alpine evaluation from asset loading:

```html
<div
    id="magewire-runtime"
    hidden
    x-data="magewireRuntime"
    x-bind="magewireRuntimeBindings"
></div>

<script
    id="magewire-script"
    src="magewire.csp.min.js"
    data-navigate-once="true"
></script>
```

The hidden element is a temporary runtime configuration host. The external
script remains an inert asset loader with no Alpine directives.

Once Alpine has initialized the host, the compatibility package moves every
generated `data-*` attribute from `#magewire-runtime` to
`#magewire-script`. The resulting script follows Livewire's normal DOM contract:

```html
<script
    id="magewire-script"
    src="magewire.csp.min.js"
    data-csrf="current-form-key"
    data-update-uri="/magewire/update"
    data-navigate-once="true"
></script>
```

Moving every `data-*` attribute, rather than only the two core attributes,
preserves attributes supplied by extensions to `magewireRuntimeBindings`.

## Runtime provider names

New integrations should use the canonical runtime providers:

| Purpose | Canonical provider | Deprecated alias |
| --- | --- | --- |
| Alpine data | `magewireRuntime` | `magewireScript` |
| Alpine bindings | `magewireRuntimeBindings` | `magewireScriptBindings` |

The deprecated providers delegate to their canonical runtime equivalents, so
existing markup continues to initialize. They should only be retained while an
integration migrates; do not use them in new templates or extensions.

## Initialization order

The transfer uses the `alpine:initialized` event intentionally:

1. Livewire begins startup and schedules its script-placement diagnostic.
2. Livewire dispatches `livewire:init`.
3. `Alpine.start()` dispatches `alpine:init`.
4. Magewire registers `magewireRuntime`, `magewireRuntimeBindings`, their
   deprecated aliases, and its cookie utility.
5. Alpine initializes the hidden host and evaluates its bindings.
6. Alpine dispatches `alpine:initialized`.
7. During that synchronous event dispatch, the compatibility package moves the
   generated `data-*` attributes to the Magewire script.
8. `Alpine.start()` returns and Livewire dispatches `livewire:initialized`.
9. The Magewire compatibility initialization event follows.
10. Livewire's deferred diagnostic finds the configured script in its expected
    location.

There is no timer or promise between evaluating the bindings and transferring
the attributes. The transfer completes before `livewire:initialized` and before
normal Magewire requests can begin.

!!! warning "Do not send requests during `livewire:init`"
    `livewire:init` fires before Alpine evaluates the runtime host, so the script
    does not yet contain `data-csrf` or `data-update-uri` at that event. An
    integration that needs the configured runtime must wait for
    `livewire:initialized` or the corresponding Magewire initialization event.

The forwarding listener runs once. Extensions must contribute their dynamic
`data-*` bindings before Alpine finishes initializing the host; later reactive
attribute changes are not forwarded.

## Attribute ownership and extension points

Treat the three attribute categories differently:

| Attribute category | Owner | Extension point |
| --- | --- | --- |
| Asset attributes such as `src` and `data-navigate-once` | Magewire frontend-assets mechanism | `script.html_attributes` in frontend DI |
| Runtime request attributes such as `data-csrf` and `data-update-uri` | `magewireRuntimeBindings` | Magewire Alpine binding customization |
| Alpine directives such as `x-data` and `x-bind` | Runtime host | `script-alpine-js-magewire-runtime` layout block |

Static script attributes are rendered through
`FrontendAssetsViewModel::getScriptAttributes()`. Runtime attributes should be
returned as `data-*` bindings so they are evaluated on the CSP-safe host and then
forwarded to the script.

The Magento layout block `script-alpine-js-magewire-runtime` can be replaced or
moved by an integration that needs a different runtime host. Keep the stable IDs
`magewire-runtime` and `magewire-script` unless the forwarding logic is replaced
at the same time. Do not defer the runtime host past Alpine startup.

## CSRF and full-page cache safety

The CSRF value is read from the browser's current `form_key` cookie by
`magewireRuntimeBindings`. It is intentionally not embedded as a fixed
server-side value in potentially cached markup.

Moving the evaluated value to the script preserves both requirements:

- Livewire finds `data-csrf` where it expects its script configuration.
- Each browser session supplies its current form key after the page loads.

## Rules for integrations

- Do not add Alpine directives to `#magewire-script`.
- Add static script attributes through the frontend-assets configuration.
- Add dynamic request configuration as `data-*` bindings on the runtime host.
- Register runtime bindings before `alpine:initialized`.
- Do not render a second Alpine.js bundle on a page where Magewire provides it.
- Preserve the `alpine:initialized` transfer when replacing the runtime host.

If the browser reports `Evaluating expressions on a script is prohibited in the
CSP build`, inspect the rendered `#magewire-script` first. It must not contain
`x-data`, `x-bind`, or any other Alpine directive.

See [Alpine Loading](alpine-loading.md) for the broader theme-loader strategy.
