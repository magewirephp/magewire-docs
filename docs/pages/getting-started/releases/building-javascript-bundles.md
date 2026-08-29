# Building JavaScript bundles

Magewire's browser runtime is built from a pinned Livewire 3 release and the Alpine packages that
belong with it. The
[`magewirephp/magewire-bundler`](https://github.com/magewirephp/magewire-bundler) repository provides
an isolated, repeatable build that produces both standard and CSP-compatible Magewire bundles.

Each dependency patch belongs to one exact upstream version. There are no range matches or fallback
patches: changing Livewire or Alpine requires a new version directory and a reviewed patch, even
when that patch happens to be identical to the previous one.

## Prerequisites

Install Git, Bash, Node.js, and npm. The selected upstream repositories provide their own npm
lockfiles; the bundler installs from those lockfiles where they are consistent.

Clone the bundler and enter its directory:

```bash
git clone https://github.com/magewirephp/magewire-bundler.git
cd magewire-bundler
```

Run the tool with `bash`, not `sh`. The release script uses Bash-specific syntax.

## Build with Livewire's Alpine version

Check a stable Livewire 3 tag before building it:

```bash
bash magewire-release.sh check v3.7.15
bash magewire-release.sh build v3.7.15
```

The check compares `js/`, `scripts/build.js`, `package.json`, and `package-lock.json` with the last
successful build. It prints the relevant files and commits, but does not create or replace output.

By default, the build reads Livewire's `alpinejs` dependency and checks out that exact Alpine tag.
The build proceeds only when both exact version patch directories exist.

## Build with a specific Alpine version

Set `ALPINE_VERSION` for a one-off compatibility build:

```bash
ALPINE_VERSION=v3.15.11 \
    bash magewire-release.sh build v3.7.15 --force
```

The script reports both the override and Livewire's declared constraint. It then selects only
`patches/alpine/v3.15.11/` and the matching exact Livewire patch directory, builds Alpine at the
requested tag, and links those packages into the isolated Livewire checkout.

!!! warning "Test explicit Alpine overrides"

    Livewire's declared Alpine dependency is the supported default. A different version may build
    successfully while still changing browser behavior. Test Magewire directives, navigation,
    morphing, uploads, and the CSP bundle before publishing the result.

Patch names, patch SHA-256 hashes, and both dependency versions participate in change detection and
the artifact identity. An Alpine-only version or patch change therefore cannot reuse another
combination's output.

## Save versions in configuration

For a repeatable local release, edit `magewire.config`:

```bash
LIVEWIRE_REPO="https://github.com/livewire/livewire.git"
LIVEWIRE_VERSION="v3.7.15"

ALPINE_REPO="https://github.com/alpinejs/alpine.git"
ALPINE_VERSION="v3.15.11"
```

Then build the configured combination:

```bash
bash magewire-release.sh build --force
```

Leave `ALPINE_VERSION` commented out to derive it from Livewire. Environment variables take
precedence over `magewire.config`, and command-line Livewire tags take precedence over its configured
tag. An alternative configuration file can be selected with `MAGEWIRE_CONFIG=/path/to/file`.

Only stable `v3.x.y` Livewire tags are accepted. Livewire 4 requires a separately reviewed build
transform.

## What the build does

The release script:

1. Checks out the requested Livewire and Alpine tags under `build/`.
2. Reports bundle-relevant Livewire changes since the last successful build.
3. Selects numbered patches from only
   `patches/livewire/<exact-version>/` and `patches/alpine/<exact-version>/`.
4. Runs `git apply --check` immediately before every patch and stops on failure.
5. Builds Alpine, installs Livewire's dependencies, and links the pinned Alpine packages.
6. Builds the standard and CSP Magewire targets.
7. Verifies every output, source map, manifest, CSP input graph, `x-html` implementation, dynamic
   code policy, and a DOM runtime fixture.
8. Promotes the staged files to an exact, fingerprinted artifact directory and records dependency
   commits, patch names, and patch SHA-256 hashes in `.magewire-state`.

Existing output is replaced only after the staged build passes verification. A failed build leaves
the last successful version and state untouched.

The patch layout for the current release is:

```text
patches/
├── livewire/
│   └── v3.7.15/
│       └── 001-magewire-build.patch
└── alpine/
    └── v3.15.11/
        └── 001-enable-x-html.patch
```

Patch filenames have a three-digit numeric prefix and are applied in that order. Never create
directories such as `v3.15.*`, and never reuse another version's directory as a fallback.

## Output

A successful build creates:

```text
dist/livewire-v3.7.15_alpine-v3.15.11_patches-<fingerprint>/
├── magewire.js
├── magewire.csp.js
├── magewire.esm.js
├── magewire.esm.js.map
├── magewire.csp.esm.js
├── magewire.csp.esm.js.map
├── magewire.min.js
├── magewire.min.js.map
├── magewire.csp.min.js
├── magewire.csp.min.js.map
└── manifest.json
```

The fingerprint is derived from the exact dependency versions, patch names, and patch hashes.
Another version or reviewed patch set receives another directory, leaving existing release
artifacts available.

Copy the required `magewire*.js` files, source maps, and manifest into the Magewire release branch
or module that owns the published frontend assets. Generated `build/`, `dist/`, and state files
are ignored by the bundler repository.

## Alpine CSP and x-html

Magewire v3.7.15 stays on Alpine CSP v3.15.11. Its exact Alpine patch removes only:

```js
import './directives/x-html'
```

from `packages/csp/src/index.js`. The standard directives import already registered Alpine's
normal `x-html`; removing this CSP override prevents it from being replaced by the directive that
always throws an error. The generated Magewire CSP bundle still resolves `@alpinejs/csp` and must
remain free of `eval` and `new Function`.

!!! danger "Only trusted or sanitized HTML"

    Restored `x-html` interprets markup. Bind it only to trusted HTML or HTML processed by a
    reviewed sanitizer. Never render uncontrolled customer input, addresses, form values, comments,
    query-string content, or other user-provided data with `x-html`. Prefer `x-text` when markup
    is not required.

## Verification and rollback

Before publishing, perform two clean builds and compare every output hash. The automated checks
confirm `@alpinejs/csp`, the normal `x-html` implementation, absence of the CSP prohibition
message, absence of `eval` / `new Function`, and trusted `x-html`, `x-text`, events, Alpine,
and Livewire startup in a browser DOM.

Also test a Magento installation: trigger a Magewire update, navigate through checkout, add a
product, open checkout, and confirm that the browser console contains no Alpine `x-html` errors.

Keep the previous known-good distribution as a separate versioned artifact. Rollback means
deploying that artifact or rebuilding the previous exact dependency versions with their matching
patch directories. Do not roll back by manually reversing source files.

## Troubleshooting

### The build is skipped

The requested Livewire inputs match the last successful build and the output directory is complete.
Use `--force` when intentionally rebuilding, particularly after changing only `ALPINE_VERSION`:

```bash
bash magewire-release.sh build v3.7.15 --force
```

### The build appears inactive

Tag fetches and some npm installation output are quiet. Give the command time to finish and check
that the shell job has not been suspended. Run it in the foreground with Bash.

### An exact-version patch is missing or does not apply

Stop the release and review the selected upstream tag. Add a newly reviewed, numbered patch under
that dependency's exact version directory. Do not copy a patch silently, force it, use a three-way
application, broaden selection to a version range, or fall back to another directory.

### Recreate the isolated clones

Use `FRESH=1` if a disposable checkout is damaged or stale:

```bash
FRESH=1 bash magewire-release.sh build v3.7.15 --force
```
