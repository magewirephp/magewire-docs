# Tutorial: Magento Flash Messages

This walkthrough does two things at once. It shows you how to surface **flash messages** from a
Magewire component — and, because flash messages are a textbook case of a Livewire concept that
doesn't map cleanly onto Magento, it doubles as a look at **what porting a feature to Magento
actually takes**.

If you just want the API, jump to [Using it](#using-it-in-a-component). If you're curious how
Magewire bridges Laravel-isms into Magento, read on from the top.

## The problem: flash messages don't port 1:1

In Laravel/Livewire, a "flash message" is a value stashed in the **session** for exactly one request
and rendered by a Blade view:

```php
// Laravel / Livewire
session()->flash('message', 'Saved!');
```

{% raw %}
```blade
{{-- Blade --}}
@if (session('message'))
    <div class="alert">{{ session('message') }}</div>
@endif
```
{% endraw %}

Three things in there don't exist in Magento:

| Livewire assumption | Magento reality |
|---|---|
| `session()->flash()` one-request session bag | Magento has its own `MessageManager` with **typed** messages (error / warning / notice / success). |
| Blade renders the message | There is no Blade — templates are `.phtml`, and the message area is theme-owned. |
| Plain strings | Magento UI strings are translatable `\Magento\Framework\Phrase` objects (`__()`). |

So a straight port would be wrong. Magewire instead **adapts** the concept to Magento's model with
the `SupportMagentoFlashMessages` feature.

## How Magewire bridges it

The feature gives every component a `magewireFlashMessages()` collection. A component adds messages
to it during an action; the feature then ships them to the browser as an **effect**, and the theme
renders them in Magento's message area.

The flow, end to end:

1. **Collect (PHP).** Your action calls `$this->magewireFlashMessages()->make(...)`. Each message
   carries a translatable `Phrase` and one of Magento's four types.
2. **Dehydrate (PHP).** When the component dehydrates, the feature checks the collection and, if it's
   non-empty, pushes a `dispatches` effect onto the snapshot — a browser event named
   `magewire:flash-messages:dispatch` with the mapped `{ text, type }` payload.
3. **Render (JS + theme).** A theme template listens for that event and renders each message in the
   Magento-styled message area. (Hyvä ships this listener; the bridge is theme-agnostic, so any theme
   can provide one.)

Notice what changed versus Laravel: there's no session bag and no Blade. The message crosses the
wire as a **dispatched event effect** (the same effect channel Magewire uses for events), and the
*theme* owns rendering — exactly the seam Magento expects.

## Using it in a component

```php
use Magewirephp\Magewire\Component;

class SaveProfile extends Component
{
    public function save(): void
    {
        // … persist the profile …

        $this->magewireFlashMessages()->make(__('Your profile was saved.'))->asSuccess();
    }
}
```

`make()` returns a fluent `FlashMessage`, so you pick the Magento type with a builder:

```php
$this->magewireFlashMessages()->make(__('Profile saved.'))->asSuccess();
$this->magewireFlashMessages()->make(__('Could not save profile.'))->asError();
$this->magewireFlashMessages()->make(__('Some fields were ignored.'))->asWarning();
$this->magewireFlashMessages()->make(__('Heads up.'))->asNotice();   // default
```

The four builders map directly to Magento's message types:

| Builder | `FlashMessageType` |
|---|---|
| `asError()` | `error` |
| `asWarning()` | `warning` |
| `asNotice()` | `notice` (default) |
| `asSuccess()` | `success` |

### Translatable strings

Pass an `__()` phrase (or a plain string, which is wrapped in `__()` for you). Messages render
through Magento's translation layer, so they're localisable like any other Magento string:

```php
$this->magewireFlashMessages()->make(__('Saved %1 items.', $count))->asSuccess();
```

### Named messages (avoiding duplicates)

`make()` accepts a name as its third argument. Re-using a name replaces rather than appends — handy
when an action can run repeatedly within one request:

```php
$this->magewireFlashMessages()->make(__('Saving…'), FlashMessageType::Notice, 'save-status');
```

Remove one by name with `unset('save-status')`. `count()` and `fetch()` inspect the collection.

## Flash messages vs notifications

Magewire has two ways to talk to the user, and they're not the same:

- **Flash messages** (this page) — render in Magento's **native message area**, using Magento's four
  message types. Reach for these when you want output that looks and behaves like every other Magento
  notice.
- **[Notifications](../../features/notifications.md)** — a toast-style notifier addon
  (`magewireNotifications()`), independent of Magento's message area.

## The takeaway

Porting "flash messages" to Magento wasn't a copy — it was a translation: session bag → dispatched
event effect, Blade → theme-owned `.phtml`, plain strings → `Phrase`, and Livewire's single message
→ Magento's four typed messages. That's the recurring shape of bringing a Livewire feature into
Magewire: **keep the developer-facing idea, re-seat the implementation on Magento's primitives.**

## Related

- [Notifications](../../features/notifications.md) — the toast alternative.
- [Events](../../essentials/events.md) — the dispatch/effect channel flash messages ride on.
- [Examples](../examples.md) — back to the examples index.