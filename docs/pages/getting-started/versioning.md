# Versioning

This page explains how Magewire is versioned, why V2 was skipped, and how the version numbers on Magewire's subpackages relate to the core framework.

## Semantic versioning

Magewire and its released companion packages follow [semantic versioning](https://semver.org/)
(`MAJOR.MINOR.PATCH`):

- **MAJOR**: breaking changes that may require code updates.
- **MINOR**: new, backward-compatible features.
- **PATCH**: backward-compatible bug fixes.

A security patch can remove behavior that code depended on without meaning to. The 3.7.2 security release, for
example, stopped the browser from calling methods inherited from Magewire's base component. Read the
[Upgrade notes](releases/upgrade-notes.md) before applying any release.

## Why V2 was skipped

Magewire V2 never existed. Magewire V1 was built on Livewire V2, which created persistent version confusion: a "Magewire 1" that was effectively at Livewire's v2 feature line. V3 aligns Magewire's major version with Livewire's, so V2 was skipped entirely. Going forward, Magewire's major version tracks Livewire's.

## What a `3.x.x` tag means

A `3.x.x` version is **not** just the core `magewirephp/magewire` package. It means one of two things:

1. It is Magewire itself at version `3.x.x`, or
2. It is a subpackage that **requires Magewire V3 and up**.

Subpackages adopt the major version of the Magewire release they target rather than starting their own version line. So for packages like `magewirephp/magewire-hyva-theme` or `magewirephp/magewire-hyva-checkout`, there is no `1.x` or `2.x`; they are tagged `3.x` because they are packages for Magewire V3.

This keeps the ecosystem readable: if you see a `3.x` tag anywhere in the Magewire family, you know it belongs to the V3 generation.

An experimental repository without a public tag or Packagist release is not an installable subpackage and does not
inherit a support promise from this convention. Verify the selected package's published tags and Composer metadata.

## Companion package compatibility

A subpackage's minor version does not follow core's. The `magewirephp/magewire` constraint in each tag's
`composer.json` decides which core releases it installs with:

| Package | Release | Requires `magewirephp/magewire` | Other Magewire requirements |
|---|---|---|---|
| `magewirephp/magewire-hyva-theme` | 3.0.0, 3.0.1 | `>=3.2` | |
| `magewirephp/magewire-hyva-theme` | 3.1.0, 3.1.1 | `>=3.6` | |
| `magewirephp/magewire-hyva-theme` | 3.1.2 | `>=3.7` | |
| `magewirephp/magewire-hyva-checkout` | 3.0.0 | `>=3.2` | `magewirephp/magewire-hyva-theme` (any) |
| `magewirephp/magewire-hyva-checkout` | 3.1.0 | `>=3.7` | `magewirephp/magewire-hyva-theme` (any) |
| `magewirephp/magewire-hyva-checkout` | 3.1.1 | `~3.7.1` | `magewirephp/magewire-hyva-theme` (any) |
| `magewirephp/magewire-admin` | 3.0.0 | `^3.0` | |

Every listed release accepts the 3.7.2 security release. `magewirephp/magewire-hyva-checkout` 3.1.1 caps core below
3.8, so a later core minor release needs a matching checkout release. Because the checkout package accepts any Hyvä
theme package version, require `magewirephp/magewire-hyva-theme` 3.1.2 or later explicitly alongside Magewire 3.7;
older theme releases ship notifier styles written for the 3.6 markup.

## PHP version support

The `php` constraint in the tagged package's `composer.json` is authoritative. Magewire 3.7 requires PHP 8.2 or newer, while the production-build matrix verifies selected Magento and Mage-OS releases on PHP 8.2 through 8.5.

A future release may raise the minimum when ecosystem compatibility or language support requires it. Check Composer constraints and the repository's production-build workflow before planning an upgrade; do not infer support solely from PHP's general support calendar.
