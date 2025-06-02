---
title: Magewire 3 - Hello World #2
authors:
    - willem
date: 2025-06-02
tags: [V3, release]
---

## Here We Go!

A promise is a promise. I said Magewire V3 would be released a week after the docs went live,
and I'm a man who sticks to his word—even if V3 isn't quite where I'd like it to be yet.

From this point forward, we're going to build this airplane while it's getting ready to take off.
Luckily, we're still taxiing on the runway, and as long as that `beta` tag stays on,
we'll keep it grounded until it's ready to fly.

## The Journey Is What Matters Most

They say it all the time—the journey itself is more important than the destination, and that's no different with Magewire.
I've learned an incredible amount as a professional, but also as a person, during this development process.
For me, it's been such a beautiful experience to work on something where I could completely let loose on how I wanted the architecture to be.

Through all the years working with Magento 1 and Magento 2, I've always had an extreme interest in architecture and
kept challenging myself to improve, try new things, and sometimes go a bit outside the lines of old-school Magento standards.
Not everyone always appreciates that, but I figure—if I don't try it and make mistakes, how are we ever going to make
Magento attractive to the new generation of developers who really do think differently?

The road has been pretty long, and fortunately, the endpoint isn't in sight yet. Even though many people ask me why I
invest so much free time in something that doesn't pay back in a community like ours.
I can't say anything other than—this is completely true. The investment is ridiculous, and sometimes I ask myself
that same question: what am I doing all this for?

For me, the answer is simple: it makes me incredibly happy. Working on my own thing, not constantly having to worry
about what someone thinks of it, and just being able to pour all my knowledge into an ultimate project that I couldn't
imagine working without in my daily work anymore.

## Now for the Serious Stuff

V3—a lot of the same, plus some innovations that came about partly through necessary things like CSP and other things
I've had on my wishlist for a long time but could never really make happen in Magewire V1.

The architecture is solid now, but not everything that's standard in V1 is in V3 yet. There's still plenty that needs to be ported over,
but I expect this will go much faster now that all the tools are available. So over the coming months, that's roughly
the plan for the beta—to work (hopefully together) toward a version that at least contains everything V1 has.

## What's New?

Good question. There are many new features like Fragments, which let you mark sections in your PHTML and tweak them using modifiers.
Fragments came about because of CSP—I wanted a tool I could wrap around a `script` block and then optionally modify based on different variables,
like adding a `nonce` attribute or creating a hash of the content and passing it to Magento's CSP collection.
I've expanded this concept to offer other fragments in the future. You could think of feature flags, for example
where you can show part of your PHTML only based on a specific version of another package.

There's also a new `@` compiler that allows you to use so-called `@`-directives in your PHTML that
automatically get converted to valid PHP during compilation. This creates cleaner, more readable PHTML,
but also means less actual PHP code in the PHTML files. There's much less need for all kinds of View Models and Helpers to get things done.
I have some really exciting ideas in the pipeline for this feature that I hope to add soon. The groundwork is already laid.

Of course, the completely new documentation shouldn't be forgotten either. I'm glad I set this up because I can now
write about things much more specifically compared to the previous approach where everything was buried on a single
page in the Magewire repository itself. The domain name might still change to make it easier to find,
but the first steps have been taken.

There's so much innovation that I could write endlessly about it, but I think it's smarter for you to take a look at
the documentation to get a good picture of what might be relevant for you.

## Finally

I'll try to write a blog post every month about Magewire's progress, but I won't make a LinkedIn post about it every time.
So definitely keep an eye on this blog page if you're interested in more reading material about this project!

And if you feel the urge to contribute, whether through code or financially, I invite you to get in touch!
