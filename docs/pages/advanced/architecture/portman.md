# Portman

!!! warning "Portman is solely needed for development and contributions. Magewire itself runs seamlessly without requiring Portman."

Portman, developed by **Justin van Elst**, is a command-line utility designed to simplify the process of porting PHP libraries between frameworks.

## What is Portman?

The idea for Portman was born during a two-hour car ride, sparked by a discussion between Justin van Elst and Willem Poortman,
about some ideal solutions to avoid the challenges faced during the development of the Magewire 3 port from Livewire.
Throughout the process, a number of workarounds had to be implemented to make things function — many of which were less than ideal —
as Livewire wasn’t built with cross-framework compatibility in mind.

During that conversation, a rough sketch of a possible solution was made. Justin took that concept and turned it into Portman —
one of the most critical tools that made Magewire V3 possible.

Portman enables developers to perform various porting tasks without the need to overwrite original source files.
Since Magewire draws heavy inspiration from Livewire’s codebase, keeping up with upstream changes would have been
nearly impossible through manual syncing alone. Thanks to Portman’s intelligent porting capabilities,
only minimal modifications were needed to adapt Livewire’s functionality for Magento.

More details, please refer to the [GitHub repository](https://github.com/magewirephp/portman).

## Requirements

Before we start, make sure you have the following installed:

- PHP version 8.2 or later

## Installation

To start contributing to Magewire, follow these steps:

1. Require Portman via Composer:
   ```shell
   composer require magewirephp/portman --dev
   ```
2. CD into the Magewirephp module:
   ```shell
   cd vendor/magewirephp/magewire
   ```
3. Optionally, initialize a configuration when it does not exist:
   ```shell
   ../../bin/portman init
   ```
4. Optionally, download the donor source
   ```shell
   ../../bin/portman download-source
   ```
5. Build a new distribution:
   ```shell
   ../../bin/portman build
   ```
6. Optionally, use a watcher while programming:
   ```shell
   ../../bin/portman watch
   ```
   
## Watcher

The watcher will automatically trace files and rebuild a new distribution on file changes.

1. Install `chokidar-cli`:
   ```shell
   npm install chokidar-cli
   ```
2. Optionally, install it globally:
   ```shell
   npm install chokidar-cli -g
   ```
3. Run the watcher:
   ```shell
   ../../bin/portman watch
   ```

## Troubleshooting

Some common issues are:

| Issue                                                                                              | Solution                                                                                                                                           |
|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| The `/dist` folder is missing after requiring Magewire via Composer                                | The distribution is only build when a new release is being pushed. When you require Magewire manually, you need to first build a new distribution. |
| Disctribution build, but shows a warning that one or more files have a augmentation but no source. | Use `../../bin/portman download-source` and rebuild once more.                                                                                     |
