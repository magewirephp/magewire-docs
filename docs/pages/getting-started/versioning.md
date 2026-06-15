# Versioning

This page explains how Magewire is versioned, why V2 was skipped, and how the version numbers on Magewire's subpackages relate to the core framework.

## Semantic versioning

Magewire and its subpackages follow [semantic versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`):

- **MAJOR** — breaking changes that may require code updates.
- **MINOR** — new, backward-compatible features.
- **PATCH** — backward-compatible bug fixes.

## Why V2 was skipped

Magewire V2 never existed. Magewire V1 was built on Livewire V2, which created persistent version confusion — a "Magewire 1" that was effectively at Livewire's v2 feature line. V3 aligns Magewire's major version with Livewire's, so V2 was skipped entirely. Going forward, Magewire's major version tracks Livewire's.

## What a `3.x.x` tag means

A `3.x.x` version is **not** just the core `magewirephp/magewire` package. It means one of two things:

1. It is Magewire itself at version `3.x.x`, or
2. It is a subpackage that **requires Magewire V3 and up**.

Subpackages adopt the major version of the Magewire release they target rather than starting their own version line. So for packages like `magewirephp/magewire-hyva-theme` or `magewirephp/magewire-hyva-checkout`, there is no `1.x` or `2.x` — they are tagged `3.x` because they are packages for Magewire V3.

This keeps the ecosystem readable: if you see a `3.x` tag anywhere in the Magewire family, you know it belongs to the V3 generation.