<a id="admin"></a>

# Magewire in Magento Admin

<a id="when-to-install-it"></a>
<a id="no-in-core-admin-marker"></a>

Build an admin component with the same PHP class, PHTML template, and layout
argument used on the storefront. Install `magewirephp/magewire-admin` to add
the admin update route and browser integration:

```shell
composer require magewirephp/magewire-admin
bin/magento module:enable Magewirephp_MagewireAdmin
bin/magento setup:upgrade
```

<a id="what-the-package-provides"></a>

Then put the layout and template in `view/adminhtml/`:

```text
Vendor/Module/
├── Magewire/Admin/ReportFilter.php
└── view/adminhtml/
    ├── layout/vendor_module_report_index.xml
    └── templates/magewire/admin/report-filter.phtml
```

The binding still uses a direct `magewire` object argument:

```xml
<block name="vendor.module.report-filter"
       template="Vendor_Module::magewire/admin/report-filter.phtml">
    <arguments>
        <argument name="magewire" xsi:type="object" shared="false">
            Vendor\Module\Magewire\Admin\ReportFilter
        </argument>
    </arguments>
</block>
```

Choose the layout handle and parent container for the admin page you are
extending. [Building admin components](building-admin-components.md) shows a
larger example with an action and ACL check.

Admin authentication protects the update route, but it does not decide
which records a given admin user may change. Check the appropriate ACL
resource inside every sensitive action and let a Magento service enforce
the operation's business rules. The admin theme also has different CSS
and JavaScript conventions from Hyvä; do not assume Tailwind classes
or storefront script ordering are available.

<a id="where-to-go-next"></a>

See [Installation](installation.md) for verification,
[How it works](how-it-works.md) for routing and script details, and
[Admin rate limiting](rate-limiting.md) for update traffic controls.
