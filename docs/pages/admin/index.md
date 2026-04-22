# Admin

Magewire V1 was storefront-only. V3 supports the Magento **admin panel** through a separately-installed companion package: `magewirephp/magewire-admin`.

The admin ships with its own conventions — a different frontName (`/admin`), RequireJS, Prototype.js on every page, a strict login/ACL model, and no Tailwind. `magewire-admin` bridges all of that so components behave the same way they do on the storefront.

## What the package provides

| Concern | Solution |
|---|---|
| **Routing** | Custom admin route at `/admin/magewire/update` with admin session validation |
| **Authentication** | Session-cookie check via `Magento\Backend\Model\Auth\Session\Proxy` before every update |
| **Script injection** | Plugin on `Magento\Framework\View\Page\Config\Renderer` that emits Magewire's bundle *before* RequireJS |
| **Prototype.js collision** | RequireJS shim restoring `Object.keys` / `Object.values` that Prototype pollutes |
| **Component resolution** | `LayoutAdminResolver` reading admin-layout metadata under the `layout_admin` accessor |
| **Component discovery workaround** | `doesPageHaveComponents()` always returns `true` — admin JS loads too early for DOM-based discovery |

## Relation to the `themes/Backend/` marker

The core `magewirephp/magewire` package ships a marker compatibility module under `themes/Backend/`. It only exists to set area scope and enable the service provider in `adminhtml`. The real admin integration lives in `magewirephp/magewire-admin` — that is the package you install.

## When to install it

Install `magewire-admin` when you want to build admin components — grids that update without page reload, inline editors, reactive dashboards, wizards. If you only build storefront components, you don't need it.

## Where to go next

- [Installation](installation.md)
- [How it works](how-it-works.md) — architecture detail.
- [Building admin components](building-admin-components.md) — layout XML, area scoping.
- [Rate limiting](rate-limiting.md) — admin-specific template and configuration.
