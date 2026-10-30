# WEB-ANIMATIONS-1#model-liveness

**Model liveness** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

Changes made to any part of the model cause the entire timing model to be updated and any dependent style.

Unless otherwise stated, invoking the methods or constructors, or getting or setting the members of interfaces defined in the [Web Animations API](https://drafts.csswg.org/web-animations-1#web-animations-api) does *not* produce a [style change event](https://drafts.csswg.org/css-transitions-1/#style-change-event).

> **Note:** Note: Other specifications that extend this specification are expected to refine the requirements on [style change events](https://drafts.csswg.org/css-transitions-1/#style-change-event) by introducing circumstances where such events *are* triggered. For example, when the interfaces in this specification represent animations defined by CSS markup, many of their methods will need to trigger style change events in order to reflect changes to the specified style.

*This section is non-normative*Based on the above requirement and normative requirements elsewhere in this specification, the following invariants can be observed:

Changes made to the [Web Animations model](https://drafts.csswg.org/web-animations-1#web-animations-model) take effect immediately 

For example, if the [`KeyframeEffect`](https://drafts.csswg.org/web-animations-1#keyframeeffect) associated with an [`Animation`](https://drafts.csswg.org/web-animations-1#animation) is [seeked](https://drafts.csswg.org/web-animations-1#seek) (see [§ 4.5.4 Setting the current time of an animation](https://drafts.csswg.org/web-animations-1#setting-the-current-time-of-an-animation)) via the [Web Animations API](https://drafts.csswg.org/web-animations-1#web-animations-api), the value returned when querying the animation’s `startTime` will reflect updated state of the model immediately.

> **Example:** ```
> // Initially animation.effect.getComputedTiming().localTime is 3000
> animation.currentTime += 2000;
> alert(animation.effect.getComputedTiming().localTime); // Displays "5000"
> ```

Querying the computed style of a property affected by animation returns the fully up-to-date state of the animation 

For example, if the used style of an element is queried immediately after applying a new [`Animation`](https://drafts.csswg.org/web-animations-1#animation) to that element, the result of the new animation will be incorporated in the value returned.

> **Example:** ```
> // Set opacity to 0 immediately
> elem.animate({ opacity: 0 }, { fill: 'forwards' });
> alert(window.getComputedStyle(elem).opacity); // Displays "0"
> ```

Changes made within the same task are synchronized such that the whole set of changes is rendered together 

As a result of changes to the model taking effect immediately combined with ECMAScript’s run-to-completion semantics, there should never be a situation where, for example, *only* the changes to specified style are rendered without applying animation.

> **Example:** ```
> // Fade the opacity with fallback for browsers that don't
> // support Element.animate
> elem.style.opacity = '0';
> elem.animate([ { opacity: 1 }, { opacity: 0 } ], 500);
> ```

> **Note:** Note, however, that in the example above, a user agent may render a frame with *none* of the above changes applied. This might happen, for example, if rendering occurs in a separate process that is scheduled to run shortly after the above task completes but before the changes can be communicated to the process.

The value returned by the `currentTime` attribute of a [document timeline](https://drafts.csswg.org/web-animations-1#document-timeline) will not change within a task 

Due to the requirement on [timelines](https://drafts.csswg.org/web-animations-1#timeline) to update their [current time](https://drafts.csswg.org/web-animations-1#timeline-current-time) each time the [update animations and send events](https://drafts.csswg.org/web-animations-1#update-animations-and-send-events) procedure is run, querying the `currentTime` twice within a long block of code that is executed in the same script block will return the same value as shown in the following example.

> **Example:** ```
> var a = document.timeline.currentTime;
> // ... many lines of code ...
> var b = document.timeline.currentTime;
> alert(b - a); // Displays 0
> ```

The time passed to a `requestAnimationFrame` callback will be equal to `document.timeline.currentTime` 

Since HTML’s [event loop processing model](https://html.spec.whatwg.org/multipage/webappapis.html#event-loop-processing-model) defines that the procedure to [update animations and send events](https://drafts.csswg.org/web-animations-1#update-animations-and-send-events) is performed prior to [running animation frame callbacks](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html.html#run-the-animation-frame-callbacks), and since the time passed to such callbacks is the same *now* timestamp is passed to both procedures, the [current time](https://drafts.csswg.org/web-animations-1#timeline-current-time) of a the [default document timeline](https://drafts.csswg.org/web-animations-1#document-default-document-timeline) should match the time passed to `requestAnimationFrame`.

> **Example:** ```
> window.requestAnimationFrame(function(now) {
>   // Displays 0
>   alert(now - document.timeline.currentTime);
> });
> ```

Calling methods from this programming interface will generally *not* cause transitions to be triggered 

Consider the following example:

> **Example:** ```
> // Setup transition start point
> div.style.opacity = '1';
> getComputedStyle(div).opacity;
>
> // Setup transition end point
> div.style.transition = 'opacity 1s';
> div.style.opacity = '0';
>
> // Fire an animation
> div.animate({ opacity: [0.5, 1] }, 500);
>
> // Wait for the transition to end -- the following will never be called!
> div.addEventListener('transitionend', () => {
>   console.log('transitionend');
> });
> ```

In this case, calling [`animate()`](https://drafts.csswg.org/web-animations-1#dom-animatable-animate) will *not* trigger a [style change event](https://drafts.csswg.org/css-transitions-1/#style-change-event). As a result, the pending style change will be processed at the same time as the style change resulting from the new animation. Since the animation style will override the [before-change style](https://drafts.csswg.org/css-transitions-1/#before-change-style) and the [after-change style](https://drafts.csswg.org/css-transitions-1/#after-change-style), no transition will be generated and the event handler for the [transitionend](https://drafts.csswg.org/css-transitions/#transitionend) event will never be called.

## Navigation

- Parent: `programming-interface` — Programming interface
- Prev: `the-animationplaybackevent-interface` — The AnimationPlaybackEvent interface

## Outgoing refs (18)

`webspec-index refs WEB-ANIMATIONS-1#model-liveness -d outgoing -l 18`

## Incoming refs (2)

- WEB-ANIMATIONS-1#contents
- WEB-ANIMATIONS-1#the-animation-interface

### Possible effects

WEB-ANIMATIONS-1#model-liveness

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#model-liveness" --format markdown`
