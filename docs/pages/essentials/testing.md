# Testing

Magewire uses complementary checks rather than relying on browser tests alone:

- PHPUnit covers isolated PHP behavior such as the application container and registries.
- Playwright exercises Magewire in a running Magento storefront.
- The production-build matrix installs Magewire into supported Magento Open Source and Mage-OS versions and runs `setup:di:compile`.
- Static analysis and formatting workflows cover the PHP source separately.

## Unit tests

From a Magewire source checkout with Composer dependencies installed:

```shell
phpunit --bootstrap vendor/autoload.php --do-not-cache-result tests/Unit
```

The repository workflow currently runs this suite on PHP 8.2. Application modules can use their own PHPUnit integration and mock component dependencies as normal Magento services.

## Playwright

The browser suite requires a Magento installation with sample data and Magewire's Playwright fixtures enabled.

From the Magewire source checkout:

```shell
cd tests/Playwright
npm install
```

Create `tests/Playwright/.env`:

```dotenv
BASE_URL=https://local.test/
ENVIRONMENT=local
ACCOUNT_FIRSTNAME=Veronica
ACCOUNT_LASTNAME=Costello
ACCOUNT_EMAIL=roni_cost@example.com
ACCOUNT_PASSWORD=roni_cost3@example.com
```

Run the suite or open Playwright's interactive UI:

```shell
npm run test
npm run test:ui
```

Do not commit real customer credentials or a local `.env` file.

## Compatibility matrix

Magewire 3.5's production workflow verifies these representative builds:

| Distribution | Release | PHP |
|---|---:|---:|
| Magento Open Source | 2.4.6-p15 | 8.2 |
| Magento Open Source | 2.4.7-p10 | 8.3 |
| Magento Open Source | 2.4.8-p5 | 8.4 |
| Magento Open Source | 2.4.9 | 8.5 |
| Mage-OS | 1.3.1 | 8.2 |
| Mage-OS | 2.3.0 | 8.4 |
| Mage-OS | 3.2.0 | 8.5 |

This matrix demonstrates tested combinations, not every theoretically installable permutation. Check the workflow in the tag you deploy.
