# FAQ

## What is Magewire?

MagewirePHP brings the power of reactive, server-driven UI development to Magento 2—without writing JavaScript.
Inspired by Laravel Livewire, MagewirePHP lets you build dynamic, interactive frontend components using only PHP,
fully integrated with Magento’s architecture.

Whether you're creating real-time search, dynamic product forms, or interactive checkout steps, MagewirePHP enables a clean,
component-based approach that stays true to Magento’s conventions while simplifying complex frontend behavior.

MagewirePHP helps you deliver modern UX experiences in Magento—faster, cleaner, and with less frontend overhead.

## Why Use Magewire?

Apart from a few frameworks attempting to mimic Magewire's concept, it is a proven framework not only within the Magento community but,
more importantly, within the Laravel community, where it has become one of the most widely used third-party frameworks.

With approximately 3,000 weekly downloads of Magewire V1, Magewire V3 is poised to surpass that record.

## When Is Magewire the Right Choice?

Magewire doesn’t make sense everywhere, but with Magewire V3, it has become much more feature-rich.
It no longer just makes blocks dynamic; it offers a variety of powerful features, making it a great choice in certain situations.

We like to describe a Magewire component as a "View Model on steroids." While providing examples can be helpful,
it might limit developers' creativity and detract from the curiosity we aim to foster.

If we offer a list of examples that doesn’t suit your needs, you might overlook the framework entirely.
However, with just a little exploration, Magewire could be the perfect fit for your project.

## What Are the Key Differences Between Magewire V1 and V3?

Magewire V1 started as an experiment that quickly gained traction, especially after Hyvä embraced the framework for its products.
Others soon followed, building filtering systems, configurators, and quick order components on top of it.
Over time, a lot was built on the framework—despite it not being originally designed to support such a wide range of features.

Magewire V3, however, is a different story. It has been developed with a structure much closer to Livewire V3,
reusing a significant amount of its core code. A thin wrapper integrates it seamlessly into Magento,
making upgrades easier and enabling a more modular approach to building new features.

Additionally, a custom router was introduced to improve performance, resulting in a notable ~33% performance gain.

## What Will Happen to Magewire V1?

Active development on this project has ceased, meaning no new features will be added.

Merge requests are still welcome, and bug fixes may be addressed depending on the time investment required.

Security updates will continue to be applied until **January 1st, 2026.**

## Are All Features from V1 Already Available in V3?

At the time of writing, this is not yet the case. However, the most commonly used features are already available.

While there is never a perfect time to release V3, the current architecture makes porting features and ensuring compatibility easier than ever.

## Can I Upgrade from Magewire V1 to V3?

Using the upgrade guide should get you most of the way there. However, you might still encounter some issues — in those cases,
we encourage you to troubleshoot them yourself or reach out for support on our Discord.

*If you encounter any issues while upgrading, please report them via GitHub Issues.*

## Can Magewire Be Used with the Luma Theme?

Magewire has been specifically designed to be Hyvä-first, meaning it works seamlessly with the Hyvä theme right out of the box.

That said, thanks to its flexible architecture, Magewire can also be made compatible with other themes. In fact, it has already been made compatible with the admin panel.

## Will Hyvä Checkout Use Magewire V3?

Magewire is an independent framework, with support from Hyvä through contributions to areas necessary for its products.

Whether it will be officially supported is beyond our control, so we cannot make any guarantees or statements about that.

## Can V1 and V3 run simultaneously?

No, this is not possible. Magewire V3 is a complete rewrite, though it maintains backward compatibility where feasible.

However, features that were specifically built for Magewire V1 will need to be updated to work with V3.

The upgrade process shouldn't be difficult—just follow the steps outlined in the [Upgrade Guide](upgrade.md),
which will help you migrate your code smoothly.

## Where can I find the V1 Documentation?

V1 documentation can be found [here](https://github.com/magewirephp/magewire/tree/1.13.1/docs)
