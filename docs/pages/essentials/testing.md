# Testing

!!! info "Magewire's test coverage is currently limited, focusing primarily on Playwright tests. We plan to expand testing in the future to include unit tests and other test types as needed."

## Playwright

Playwright is an open-source automation library developed by Microsoft for testing and automating web applications.
It enables developers to write reliable end-to-end tests by simulating user interactions across multiple browsers,
including Chromium, Firefox, and WebKit. Playwright supports various programming languages like JavaScript, TypeScript,
Python, and C#, and provides features such as auto-waiting, network interception, and mobile emulation.
It is widely used for ensuring web application functionality and performance.

### Requirements

Before we start, make sure you have the following installed:

- Magewire 3.0.0 or later
- Magento version 2.4.4 or later

### Installation

1. CD into the Playwright test folder
   ```shell
   cd vendor/magewirephp/magewire/tests/Playwright
   ```

2. Install all dev-dependencies
   ```sh
   npm install
   ```

3. Create a `.env` config file in the root `Playwright` folder using the following variables:
   ```text
   BASE_URL=https://local.test/
   
   ENVIRONMENT=local
   ACCOUNT_FIRSTNAME=Veronica
   ACCOUNT_LASTNAME=Costello
   ACCOUNT_EMAIL=roni_cost@example.com
   ACCOUNT_PASSWORD=roni_cost3@example.com
   ```
   _Set the `BASE_URL` value with the `base-url` of your Magento instance._

4. Run tests
   ```sh
   npm run test
   ```

5. Run tests manually (optional)
   ```sh
   npx playwright test --ui
   ```
