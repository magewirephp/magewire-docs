# How It Works

`magewire-admin` is thin — five PHP classes and a handful of XML files. This page walks through each piece so you know what to look for when something goes wrong.

## The admin route

```xml title="etc/adminhtml/routes.xml"
<router id="admin">
    <route id="magewire" frontName="magewire">
        <module name="Magewirephp_Magewire" before="Magento_Backend"/>
    </route>
</router>
```

Registers `/admin/magewire/update` as the POST target for admin component updates. The `admin` router id means the route lives behind the admin's URL prefix (typically `/admin`, renamed via the Magento admin URL setting).

## Admin session check

```php title="Controller/MagewireUpdateRouteAdminhtml.php"
class MagewireUpdateRouteAdminhtml extends MagewireUpdateRouteFrontend
{
    public function getMatchConditions(): array
    {
        return array_merge([
            'auth' => fn (Request $request): bool =>
                $this->sessionAuth->getSessionId() === $request->getCookie(AdminConfig::SESSION_NAME_ADMIN)
        ]);
    }
}
```

The admin controller swaps the storefront's match conditions for an `auth` check: the admin session cookie (`AdminConfig::SESSION_NAME_ADMIN`) must match the active admin session. Requests from a logged-out browser are rejected before the component pipeline runs. The session service is injected as `Magento\Backend\Model\Auth\Session\Proxy` via DI.

## Script injection before RequireJS

The admin renders RequireJS and Prototype.js inline-early. Magewire's own `<script>` must load **before** those, or the inline setup scripts run against an uninitialised Magewire.

```php title="Plugin/Magento/Framework/View/Page/Config/Renderer.php"
public function afterRenderAssets(Subject $subject, string $result): string
{
    $head = $this->layout->getBlock('magewire.head');

    if ($head) {
        return preg_replace('/(<script\b[^>]*>)/i', $head->toHtml() . '$1', $result, 1);
    }

    return $result;
}
```

The plugin runs after Magento assembles the head assets and injects the `magewire.head` block right before the first `<script>` tag. `LayoutInterface` is injected directly into the plugin.

## Layout

```xml title="view/adminhtml/layout/default.xml"
<body>
    <move element="magewire" destination="root"/>

    <block name="magewire.head"
           template="Magewirephp_MagewireAdmin::js/magewire/head.phtml">
        <block name="magewire.script"
               as="script"
               template="Magewirephp_MagewireAdmin::js/magewire/head/script.phtml">
            <arguments>
                <argument name="view_model" xsi:type="object">
                    Magewirephp\Magewire\ViewModel\Magewire
                </argument>
            </arguments>
        </block>
    </block>

    <referenceBlock name="magewire.features.support-magewire-rate-limiting"
        template="Magewirephp_MagewireAdmin::magewire-features/support-magewire-rate-limiting/support-magewire-rate-limiting.phtml"/>
</body>
```

Moves the `magewire` block to root so its children render in the admin's layout tree, declares a standalone `magewire.head` block (picked up and injected by the Renderer plugin), and overrides the rate-limiting feature template with an admin-styled variant.

## Admin component resolver

```php title="Magewire/Mechanisms/ResolveComponents/ComponentResolver/LayoutAdminResolver.php"
class LayoutAdminResolver extends LayoutResolver
{
    protected string $accessor = 'layout_admin';
}
```

Extends the storefront's `LayoutResolver` and only overrides the internal `$accessor` string. The admin resolver is registered in `etc/adminhtml/di.xml` with `sortOrder="99800"` so it runs before the default layout resolver in the adminhtml area. The accessor (`layout_admin`) is stored in the snapshot memo so the same resolver is picked on subsequent `/magewire/update` roundtrips. Layout XML still binds components with `<argument name="magewire" xsi:type="object">` — identical to storefront.

## Always-on component detection

```php title="Magewire/Mechanisms/ResolveComponents/ResolveComponentsViewModel.php"
class ResolveComponentsViewModel extends CoreResolveComponentsViewModel
{
    public function doesPageHaveComponents(): bool
    {
        return true;
    }
}
```

On the storefront, Magewire's JavaScript skips full initialisation if the page has no components. On the admin, the JS runs early — **before** the DOM nodes containing `wire:snapshot` are rendered. So the check is forced to `true` and Magewire always fully initialises.

## Prototype.js collision

Prototype.js replaces `Object.keys` and `Object.values` with non-standard implementations that break a lot of modern JS, including Magewire. `magewire-admin` ships a RequireJS shim that restores the native versions before Magewire's bundle runs.

## Update URI prefix

```php title="Model/View/Utils/Magewire.php"
public function getUpdateUri(): string
{
    return '/' .
        $this->deploymentConfig->get(BackendConfigOptionsList::CONFIG_PATH_BACKEND_FRONTNAME) .
        parent::getUpdateUri();
}
```

Storefront Magewire posts to `/magewire/update`. In admin, it needs to post to `/{adminFrontName}/magewire/update` so Magento's router matches the admin routes config. This override reads the configured admin frontName from `env.php` at runtime.

## Request flow

```
Browser (admin panel)
    │
    ▼
POST /{adminFrontName}/magewire/update
    │
    ▼ Matched by admin router, routed to MagewireUpdateRouteAdminhtml
    │
    ▼ getMatchConditions() validates admin session cookie
    │
    ▼ Parent MagewireUpdateRouteFrontend runs
    │
    ▼ Snapshot checksum validated
    │
    ▼ LayoutAdminResolver reconstructs component from layout_admin metadata
    │
    ▼ Component pipeline runs (hydrate → action → render → dehydrate)
    │
    ▼ Response returned
```

## Related

- [Installation](installation.md)
- [Building admin components](building-admin-components.md)
- [Mechanisms](../advanced/architecture/mechanisms/index.md)
