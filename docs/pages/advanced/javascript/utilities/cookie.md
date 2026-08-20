# Cookie Utility

The cookie utility provides a small wrapper for reading, writing, and removing browser cookies:

```javascript
const cookie = window.MagewireUtilities.cookie
```

Use the methods exposed by the installed Magewire version rather than importing the utility's source file directly. The utility is registered before `magewire:init`, so integrations can access it from that event:

```javascript
document.addEventListener('magewire:init', () => {
    const cookie = window.MagewireUtilities.cookie

    // Use cookie.get(), cookie.set(), or cookie.getFormKey() as needed.
})
```

The utility exposes `get(name)`, `set(name, value, days)`, and `getFormKey()`. It does not provide a dedicated removal method; expire a non-sensitive cookie through normal browser-cookie semantics if your integration needs that behavior.

Cookie values remain browser-controlled input. Do not use them as proof of authentication, authorization, or trusted component state.
