# Building JavaScript bundles

Magewire's browser runtime is built from a pinned Livewire 3 release and the Alpine packages that
belong with it. The
[`magewirephp/magewire-bundler`](https://github.com/magewirephp/magewire-bundler) repository provides
an isolated, repeatable build that produces both standard and CSP-compatible Magewire bundles.

Use the declared Alpine version for routine Livewire updates. An explicit Alpine override is useful
when testing or releasing a specific combination, but that combination must be tested as a unit.

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
This keeps Alpine and all `@alpinejs/*` packages on the version declared by the selected Livewire
release.

## Build with a specific Alpine version

Set `ALPINE_VERSION` for a one-off compatibility build:

```bash
ALPINE_VERSION=v3.15.11 \
    bash magewire-release.sh build v3.7.15 --force
```

The script reports both the override and Livewire's declared constraint. It then builds Alpine at
the requested tag and links those packages into the isolated Livewire checkout before producing the
Magewire bundles.

!!! warning "Test explicit Alpine overrides"

    Livewire's declared Alpine dependency is the supported default. A different version may build
    successfully while still changing browser behavior. Test Magewire directives, navigation,
    morphing, uploads, and the CSP bundle before publishing the result.

Use `--force` for an explicit Alpine build. Change detection is based on Livewire's bundle inputs,
so an Alpine-only version change can otherwise reuse an existing complete output for the same
Livewire tag.

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
3. Builds the Alpine monorepo.
4. Applies `magewire.patch` to Livewire's build script.
5. Installs Livewire's dependencies and links the pinned Alpine packages.
6. Builds the standard and CSP Magewire targets.
7. Verifies every output, its source-map reference, the manifest, and esbuild metadata proving that
   only CSP targets resolved `@alpinejs/csp`.
8. Promotes the verified files to `dist/<livewire-tag>/` and records `.magewire-state`.

Existing output is replaced only after the staged build passes verification. A failed build leaves
the last successful version and state untouched.

## Output

A successful build creates:

```text
dist/v3.7.15/
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

Copy the required `magewire*.js` files, source maps, and manifest into the Magewire release branch or
module that owns the published frontend assets. Generated `build/`, `dist/`, and state files are
ignored by the bundler repository.

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

### `magewire.patch` does not apply

The selected Livewire release changed `scripts/build.js`. Stop the release and review that upstream
change before updating `magewire.patch`; do not blindly force or three-way apply the old transform.
The patch owns Magewire output names, CSP resolver substitution, alias resolution, and esbuild
metadata used by verification, so all of those behaviors must remain intact.

### Recreate the isolated clones

Use `FRESH=1` if a disposable checkout is damaged or stale:

```bash
FRESH=1 bash magewire-release.sh build v3.7.15 --force
```
