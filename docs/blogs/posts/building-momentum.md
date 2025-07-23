---
title: Magewire 3 - July Update #1
authors:
    - willem
date: 2025-07-23
tags: [V3, update, July]
---

# Building Momentum Behind the Scenes

The GitHub repo might look a bit quiet lately, and there's truth to that. I've been spending some extra time with my family,
the weather's been too nice to stay inside coding all day, and honestly, I wanted to give some other priorities around
the house a bit of attention for once.

But don't worry—I haven't been slacking off completely. Those evening hours have been packed with Magewire development,
and some pretty exciting features are coming your way. Most of them are already documented, but they're not in the main branch just yet.

## Progress Update

New features are rolling in—well, sort of new. I've been working on porting existing Livewire features (or maybe it's
better to say Laravel features) that will let you use what I'm calling "Flakes" in Magewire. Think of Flakes as UI components,
but with a name I made up because why not?

This means you'll soon be able to easily add reusable building blocks within your Magewire components in a developer-friendly way,
like `<magewire:dialog mw:name="example-dialog" :title="Example Dialog"/>`.

Don't panic—this isn't compiled on-the-fly. It's all precompiled thanks to a new PHTML compiler that's coming to Magewire.

```html title="Example_Module::example.phtml"
<div>
    <!-- Include a dialog Flake in a random template, customizable using additional
         element attributes which can be different for each flake. -->
    <magewire:dialog mw:name="registration-dialog" :title="Registration"/>
</div>
```

I've also been diving deep into CSP implementation—specifically how to add inline scripts to headers or pass a nonce for uncached pages.
I landed on what I'm calling a Fragment system. With this system, you can easily start a fragment anywhere in your PHTML
and close it whenever you want using the `start()` and `end()` methods. You can already find more about this in the documentation.

```html title="Example_Module::example.phtml"
<?php $script = $fragment->make()->script()->start() ?>
<script>
    console.log('Hello world');
</script>
<?php $script->end() ?>
```

Fragments get registered based on modifiers when we're dealing with `<script>` fragments. Again, I've focused heavily
on developer experience, and Fragments are incredibly versatile for tons of other use cases where you want to mark a
specific section within your template so others can modify it without necessarily having to override the entire template.

## Proving Its Worth

Magewire is gradually proving itself in more and more commercial products. Magewire V1 already powers a huge chunk of
the functionality behind [Hyvä CMS](https://www.hyva.io/hyva-commerce.html) and [Hyvä Checkout](https://www.hyva.io/hyva-checkout.html), and it's proving itself in the OpenPOS system built by loyal
sponsor [Zero1](https://www.zero1.co.uk/) and used by our other sponsor [Vendic](https://vendic.nl/).

We're also getting more social media mentions from folks like Mark Shust and Jakub Winkler.

This combination of exposure and real-world usage has pushed our download numbers past 700,000 this month—we're heading toward the 1 million mark!

These statistics speak for themselves. The best, most developer-friendly checkout on the market is currently running under so many shops that you can confidently say Magewire is a powerhouse framework. Others try to copy it, but without much success—especially once these products make the jump to V3, which will bring massive added value on so many levels.

## The Coming Months

Even though I'm going on vacation soon, I'm working behind the scenes to gather motivated people and see if I can put
together a team to get Magewire V3 out of beta as quickly as possible. We're not there yet, but the goal is definitely
to make this happen before the end of the year.

The objective, aside from the features I've already added and what I saw as must-haves, is to make Magewire V3 stable
and as backwards compatible as possible. On top of that, I really want to release Admin compatibility simultaneously so
Magewire can be used throughout the Magento backend too!

I'm also calling out to anyone who'd like to contribute to this project either with code or by sponsoring—feel free to reach out via Discord.
