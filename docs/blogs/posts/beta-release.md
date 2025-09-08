---
title: Magewire 3 - Beta Release #3
authors:
    - willem
date: 2025-09-08
tags: [V3, release, beta]
---

## Yes, it’s been a while

The months have flown by. On the surface the repo may have seemed quiet, but nothing could be further from the truth.

Behind the scenes, I’ve been working in a separate branch on a hefty list of additions that I absolutely wanted to
include in the upcoming beta release.

## Critical Security Vulnerability

The biggest strength of Magewire, and one of the main reasons I took on this challenge, is the incredible community already behind Livewire.
Livewire has already proven itself as one of the two biggest game changers in the Laravel community.

This means Magewire is not just another new brew of technology in the Magento ecosystem, it’s already a proven solution similar to e.g. AlpineJS.

A good example is security: on July 17th, a critical security issue was fixed in the [Livewire repository](https://github.com/livewire/livewire/security/advisories/GHSA-29cq-5w36-x7w3), and within just 10 minutes,
the same fix was applied to Magewire thanks to the way it has been built (ported).

## So What's Next?

Feature building has stopped for now. It’s time to focus on improving testing across the board, ensuring everything remains backwards compatible, and writing documentation on how to migrate.

In the meantime, I’m trying to establish a small team to speed things up. But I’ve found that asking for help and getting
valuable input is really a struggle—which I totally understand.

Open source in our money-driven community is incredibly difficult, with most people either waiting until something gets released,
or creating a clone of what Magewire already is and ending up in the same rabbit hole.

It’s somewhat discouraging, but I suppose that’s the reality :D

## So What's New?

I’d like to take you along for a look at what’s been happening, and honestly, these additions are features I’m incredibly excited about.

### Fragments

Fragments are a way to convert HTML into what we call a **fragment**, both inside your template files and even within PHP files.
At its core, it’s nothing more than wrapping a piece of HTML so you can give it a name.

The real benefit, however, lies in what you can do with it afterwards.
For example, you can treat a fragment directly as a CSP block whenever it involves a `<script></script>`.
And thanks to modifiers, you can centrally manage your fragments without touching a single template.

Fragments were initially intended as a better solution to make scripts CSP-compliant.
However, they eventually grew into much more, where they are no longer only needed for CSP or for wrapping `<script>` elements.

```html
<?php $script = $magewireFragment->make()->script()->start() ?>
<script>
    ...
</script>
<?php $script->end() ?>
```

Please refer to the [documentation](../../pages/concepts/fragments.md) for more details.

### Template Directives

As you might know from Laravel, Magewire now also supports the use of `@` directives inside your Magewire component templates.

Simply put: if you want to display something inside your component only to a logged-in user, you can just wrap it with `@auth` and `@endauth`.

The nice part is that this system is built in such a way that you can extend it with your own prefixes.

For example, you could create a `@{agencyNameGoesHere}CustomerGroup(1)` directive, which ensures content is only shown when the
customer is logged in and belongs to customer group 1. This directive would then belong to the magento group.

And don’t worry: thanks to the built pre-compiler, everything is precompiled into actual PHP in advance, so nothing happens on the fly.

```html
<div>
    @guest
        <!-- Will only be shown to guests. -->
        <span>Hi guest</span>
    @endguest
</div>
```

Please refer to the [documentation](../../pages/features/magewire-template-directives.md) for more details.

### Flakes

I really wanted to create a “good” system that lets you easily add re-usable components inside your Magewire components
using nothing more than simple HTML syntax. No complicated stuff, no need for additional ViewModels or other workarounds,
just like in the following example.

```php
class Dialog extends Component
{
    public string $title = '';

    public function mount(string $fooBar, AbstractBlock $block)
    {
        //
    }
}
```

Where your template simply looks like this:

```php
<?php $title = 'Hello World'; ?>

<magewire:dialog name="my-component" prop:title="$title" mount:block="$block" mount:foo-bar="baz" />
```

As you can see, you can easily inject public properties, pass mount method arguments, and use template variables as an attribute value.

Please refer to the [documentation](../../pages/features/magewire-flakes.md) for more details.

### Stream Directive

The Streaming feature has been made compatible and now works within Magewire.

Thanks to the **Portman** tool we built, it only took about 15 minutes to get it running.

Fortunately, this feature isn’t too complicated, but it does provide you with some cool new options.

Please refer to the [documentation](../../pages/html-directives/wire-stream.md) for more details.

### Rate Limiting

Livewire does not officially support this, but for many reasons I felt it was needed, so I went ahead and built it.

Rate limiting can now be applied in multiple ways. One option is via the frontend using `wire:mage:throttle`,
where most of the handling happens on the client side. This is not bulletproof, though, since a smart user could easily work around it.

That’s why server-side rate limiting has also been added. Based on system configuration, you can now limit the number of
subsequent requests within a specific time window.

Cool thing, by default its cache driven, but you can build your own adapter if you'd like.

### Observer Events

It’s not always easy to learn a new framework, I know that. That’s why, wherever possible, we should provide an approach
that already feels familiar to you as a Magento developer.

For every hook you can tap into, an observer event is automatically dispatched. This means you don’t have to create a
separate **Feature** for just a small tweak. Instead, you can simply add an event in your `events.xml` and use the provided
Data Transfer Object (DTO) to pass data along to the hook.

Please refer to the [documentation](../../pages/essentials/events.md) for more details.

### Backend Compatibility

Yes, Magewire is coming to the backend. All you need to do is require the new module `magewirephp/magewire-admin`.

I’m currently wrapping up the final details, and then nothing will hold us back from using this powerhouse of a framework in the backend as well.
