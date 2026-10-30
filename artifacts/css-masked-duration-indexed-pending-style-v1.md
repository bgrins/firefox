# CSS-ANIMATIONS-2#requirements-on-pending-style-changes

**Requirements on pending style changes** (heading)

**SHA**: hash:2f3a65bc90db82e56cc0b26890a026af8c02f356e10e4bfd03e024536a243e5c

## Content

Various operations may affect the [computed values](CSS-CASCADE-5#computed-value) of properties on elements. User agents may, as an optimization, defer recomputing these values until it becomes necessary. However, all operations included in programming interface defined in this specification, as well as those operations defined in Web Animations \[WEB-ANIMATIONS\] that may return objects or animation state defined by this specification, must produce a result consistent with having fully processed any such pending changes to computed values.

> **Note:** As an example, in the following code fragment, when the specified style of `elem` is initially updated, a user agent may defer recalculating the computed value of the [animation](CSS-ANIMATIONS-1#propdef-animation) property.However, the [`getAnimations()`](WEB-ANIMATIONS-1#dom-animatable-getanimations) method called on `elem` is specified by Web Animations and can return [`CSSAnimation`](CSS-ANIMATIONS-2#cssanimation) objects as defined in this specification. Hence, as result of the requirements in this section, the user agent must calculate the updated value of `elem`’s [animation](CSS-ANIMATIONS-1#propdef-animation) property and create the requested [`CSSAnimation`](CSS-ANIMATIONS-2#cssanimation) object before returning its result.
>
> ```
> elem.style.animation = 'fadeOut 1s';
> elem.getAnimations()[0].pause();
> ```
>
> Similarly, reading [`playState`](WEB-ANIMATIONS-1#dom-animation-playstate) may depend on pending style changes.
>
> ```
> elem.style.animation = 'fadeOut 1s paused';
> const anim = elem.getAnimations()[0];
> elem.style.animationPlayState = 'running';
> console.log(anim.playState); // Should be 'running'.
> ```

## Navigation

- Parent: `interface-dom` — DOM Interfaces
- Prev: `the-CSSAnimation-interface` — The CSSAnimation interface

## Outgoing refs (5)

`webspec-index refs CSS-ANIMATIONS-2#requirements-on-pending-style-changes -d outgoing -l 5`

## Incoming refs (1)

- CSS-ANIMATIONS-2#contents

### Possible effects

CSS-ANIMATIONS-2#requirements-on-pending-style-changes

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-ANIMATIONS-2#requirements-on-pending-style-changes" --format markdown`
