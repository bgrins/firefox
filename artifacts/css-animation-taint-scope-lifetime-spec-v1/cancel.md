# WEB-ANIMATIONS-1#cancel-an-animation

**cancel an animation** (algorithm)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

The procedure to **cancel an animation** for *animation* is as follows:

1. If *animation*’s [play state](https://drafts.csswg.org/web-animations-1#animation-play-state) is *not* [idle](https://drafts.csswg.org/web-animations-1#play-state-idle), perform the following steps:

    1. Run the procedure to [reset an animation’s pending tasks](https://drafts.csswg.org/web-animations-1#animation-reset-an-animations-pending-tasks) on *animation*.
    2. [Reject](https://webidl.spec.whatwg.org/#reject) the [current finished promise](https://drafts.csswg.org/web-animations-1#current-finished-promise) with a [`DOMException`](https://webidl.spec.whatwg.org/#idl-DOMException) named "[`AbortError`](https://webidl.spec.whatwg.org/#aborterror)".
    3. Set the \[\[PromiseIsHandled\]\] internal slot of the [current finished promise](https://drafts.csswg.org/web-animations-1#current-finished-promise) to true.
    4. Let [current finished promise](https://drafts.csswg.org/web-animations-1#current-finished-promise) be [a new promise](https://webidl.spec.whatwg.org/#a-new-promise) in the [relevant Realm](https://html.spec.whatwg.org/multipage/webappapis.html#concept-relevant-realm) of *animation*.
    5. [Create](https://dom.spec.whatwg.org/#concept-event-create) an [`AnimationPlaybackEvent`](https://drafts.csswg.org/web-animations-1#animationplaybackevent), *cancelEvent*.
    6. Set *cancelEvent*’s [`type`](https://dom.spec.whatwg.org/#dom-event-type) attribute to [cancel](https://drafts.csswg.org/web-animations-1#cancel-event).
    7. Set *cancelEvent*’s [`currentTime`](https://drafts.csswg.org/web-animations-1#dom-animationplaybackevent-currenttime) to `null`.
    8. Let *timeline time* be the [current time](https://drafts.csswg.org/web-animations-1#timeline-current-time) of the [timeline](https://drafts.csswg.org/web-animations-1#timeline) with which *animation* is associated. If *animation* is not associated with an [active timeline](https://drafts.csswg.org/web-animations-1#active-timeline), let *timeline time* be an [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) [time value](https://drafts.csswg.org/web-animations-1#time-value).
    9. Set *cancelEvent*’s [`timelineTime`](https://drafts.csswg.org/web-animations-1#dom-animationplaybackevent-timelinetime) to *timeline time*. If *timeline time* is [unresolved](https://drafts.csswg.org/web-animations-1#unresolved), set it to `null`.
    10. If *animation* has a [document for timing](https://drafts.csswg.org/web-animations-1#animation-document-for-timing), then append *cancelEvent* to its document for timing’s [pending animation event queue](https://drafts.csswg.org/web-animations-1#pending-animation-event-queue) along with its target, *animation*. If *animation* is associated with an [active timeline](https://drafts.csswg.org/web-animations-1#active-timeline) that defines a procedure to [convert timeline times to origin-relative time](https://drafts.csswg.org/web-animations-1#timeline-time-to-origin-relative-time), let the [scheduled event time](https://drafts.csswg.org/web-animations-1#scheduled-event-time) be the result of applying that procedure to *timeline time*. Otherwise, the scheduled event time is an [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) [time value](https://drafts.csswg.org/web-animations-1#time-value).

        Otherwise, [queue a task](https://html.spec.whatwg.org/multipage/webappapis.html#queue-a-task) to [dispatch](https://dom.spec.whatwg.org/#concept-event-dispatch) *cancelEvent* at *animation*. The task source for this task is the [DOM manipulation task source](https://html.spec.whatwg.org/multipage/webappapis.html#dom-manipulation-task-source).
2. Make *animation*’s [hold time](https://drafts.csswg.org/web-animations-1#animation-hold-time) [unresolved](https://drafts.csswg.org/web-animations-1#unresolved).
3. Make *animation*’s [start time](https://drafts.csswg.org/web-animations-1#animation-start-time) [unresolved](https://drafts.csswg.org/web-animations-1#unresolved).

## Navigation

- Parent: `canceling-an-animation-section` — Canceling an animation
- Next: `animation-reset-an-animations-pending-tasks` — reset an animation’s pending tasks

## Outgoing refs (29)

`webspec-index refs WEB-ANIMATIONS-1#cancel-an-animation -d outgoing -l 29`

## Incoming refs (3)

- WEB-ANIMATIONS-1#index-defined-here
- WEB-ANIMATIONS-1#the-animation-interface
- WEB-ANIMATIONS-1#updating-the-finished-state

Makes 4 calls: `webspec-index state WEB-ANIMATIONS-1#cancel-an-animation --calls`
