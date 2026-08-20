# Request Bundling

{{ include("admonition/livewire-reference.md", reference_url="https://livewire.laravel.com/docs/3.x/bundling") }}

Magewire collects component commits created in the same short browser window and sends compatible commits in one HTTP
request. Each component keeps its own snapshot and response effects; bundling changes the transport, not component
ownership.

For example, two updates initiated in the same browser task can share one call to Magewire's update route:

```html
<button type="button" wire:click="refreshTotals">Refresh totals</button>
<button type="button" wire:click="refreshAvailability">Check availability</button>
```

The browser runtime waits approximately five milliseconds before forming request pools. Do not write application logic
that depends on two user interactions always landing in the same bundle: browser timing, isolation, and an in-flight
request can place them in separate requests.

## Nested components

Layout nesting alone does not make component updates atomic. The browser runtime can co-locate parent and child commits
when their snapshots contain prop or binding metadata that requires coordinated updates. Independent components may
bundle as a transport optimization, but they still render and dehydrate separately.

Lazy components are isolated by default, so their first load normally receives its own request. Set the lazy-loading
attribute's `isolate` option to `false` only when that request may safely bundle with other work. See
[Lazy Loading](lazy-loading.md).

## Operational consequences

- One failed HTTP request can affect every commit carried by that pool.
- A bundle can be larger than a single-component update, so inspect the `components` array when profiling payloads.
- Under request rate limiting, **shared** scope consumes one attempt per bundled request, while **isolated** scope tracks
  the component identifiers inside it.
- Authorization and validation still run per public action; bundling is not a transaction or a security boundary.

Use the browser network panel to see whether updates actually bundled. See [Rate Limiting](rate-limiting.md),
[Performance](../advanced/performance.md), and [Request Filters](../advanced/request-filters.md) for server-side behavior.
