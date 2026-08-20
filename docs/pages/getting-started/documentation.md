# Documentation

Magewire is built around Livewire 3 concepts and reuses a substantial part of its runtime. The
[Livewire 3 documentation](https://livewire.laravel.com/docs/3.x/quickstart) is therefore the canonical explanation for
shared concepts such as properties, actions, morphing, and most `wire:` directives.

These Magewire docs complement that reference with Magento integration, Magewire-specific features, supported
boundaries, and differences from Livewire. Links are pinned to `/docs/3.x/` because unversioned Livewire pages can move
to a later major version that does not describe Magewire 3.

## Compatibility boundary

The Magewire repository contains ported upstream classes so changes remain traceable, but the presence of a class in
the source tree does not by itself make a feature supported. Runtime registration, Magewire's public component API,
tests, and released companion packages determine the supported surface.

| Documentation label | Meaning |
|---|---|
| Livewire reference | The linked Livewire 3 behavior applies; the local page describes Magewire differences. |
| Magewire specific | Magewire or the named companion package implements the behavior. |
| Experimental | The behavior exists, but its API or integration is not stable enough for a production promise. |
| Unsupported | Upstream code may be present, but Magewire does not currently document the feature as usable. |

Laravel services and integrations that Magewire does not register remain outside this compatibility promise. If these
docs and a tagged Magewire release disagree, the tagged source is authoritative and the docs should be corrected.

## Documentation structure

Navigation broadly follows the Livewire 3 documentation so developers familiar with Livewire can find the equivalent
concept quickly. We avoid copying upstream manuals. A shared page contains the upstream reference followed only by
Magewire-specific setup, examples, limitations, or migration notes.

{{ include("admonition/livewire-reference.md", reference_url="#") }}

Magewire-only pages use a versioned marker:

{{ include("admonition/magewire-specific.md", since_version="3.0.0") }}

Unstable behavior is marked explicitly:

{{ include("admonition/magewire-experimental.md") }}

## Writing guidelines

Write for developers who understand Magento but may be new to Magewire:

- Lead with what the feature does and when to use it.
- Prefer a small, runnable Magento example over abstract pseudocode.
- Use `we` for project decisions and `you` for instructions to the reader.
- Keep terminology, paths, namespaces, and version numbers consistent with the current release.
- Explain platform-specific limits next to the behavior they affect.
- Escape customer-visible output in `.phtml` examples and call out authorization boundaries for public actions.
- Link to Livewire 3 for shared behavior instead of reproducing it.

Concise pages are welcome when the upstream reference is complete, but a Magewire page should still answer why the
topic is present and whether Magento changes how it is used.

## Source verification

Before documenting behavior, verify it in this order:

1. Check the latest tagged `magewirephp/magewire` source and release history.
2. Confirm the Feature, Mechanism, directive, or hook is registered at runtime.
3. Check tests and the generated browser bundle for the actual request-side behavior.
4. Inspect the relevant companion repository for theme, checkout, or admin integrations.
5. Compare with Livewire 3 only after establishing the Magewire boundary.

Do not infer support from a ported class, an old V1 example, or an internal comment alone.

## Using AI as a writing aid

AI can help improve structure and wording, but technical claims and code still require human review against the source.
Do not ask a model to fill an unknown API from convention: mark the gap, investigate it, and document only what can be
verified.

A useful editing prompt is:

```text
Review the following Magewire documentation for clarity, structure, and consistency.
Preserve its technical meaning and Magento terminology. Do not invent APIs, support
claims, version numbers, or code. Keep Livewire 3 as the reference for shared behavior
and retain only Magewire-specific detail locally. Return the revised passage followed
by a short list of statements that still need verification against source or tests.
```

## Contributing

If information is missing, unclear, or outdated, see [Contribute](contribute.md). A focused correction with a source,
test, release, or reproducible example is especially helpful.
