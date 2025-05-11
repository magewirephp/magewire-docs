# Notables

Notables are brief, helpful insights that highlight useful context or nuances. They’re not meant to be buried in the main text,
nor do they require a full deep-dive explanation — they simply make small but important details clearer at a glance.

## The Magewire Block

We aim to keep JavaScript-related .phtml files as minimal and clean as possible. These templates are architected to live
within a wrapping `magewire` block, which comes with both benefits and trade-offs. One such trade-off is that many of
these blocks require the `Magewirephp\Magewire\ViewModel\Magewire` view model to function properly.

Manually assigning a `view_model` argument to each block would not only be tedious but would also result in a significant
increase in XML configuration lines. To address this, Magewire includes a small feature that automatically injects the
`view_model` argument into all sibling blocks contained within a `magewire` block.

In practice, this means that as long as your block resides inside the `magewire` block—whether directly or as a
sibling—you can access the view model via `$block->getViewModel()` or `$block->getData('view_model')`.

However, please note: if you move a block outside the `magewire` wrapper block, you'll need to manually bind the
`view_model` argument. This is precisely why the view model is passed as an argument instead of being exposed as
a global dictionary variable—to avoid forcing developers to rewrite the template just to maintain compatibility.
