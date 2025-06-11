# Patterns

!!! warning "While entirely optional, these patterns serve as recommended approaches. They’re open to discussion and improvement—as we’re always learning and evolving to make Magewire better for everyone."

Instead of sharing numerous GitHub Gists, we prefer to share the patterns used within the Magewire core package itself.
These patterns are the result of extensive experimentation and refinement, carefully crafted to keep things clean,
consistent, and maintainable.

## Magewire object on init event

While waiting for Magewire to initialize, you can import any function from the global Magewire object.

```js
document.addEventListener('magewire:init', event => {
    // This shows only a small subset of available options
    const { addons, utilities, dispatch, on } = event.detail.magewire;
});
```

