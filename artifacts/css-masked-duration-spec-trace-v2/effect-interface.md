# WEB-ANIMATIONS-1#the-animationeffect-interface

**The AnimationEffect interface** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

[Animation effects](https://drafts.csswg.org/web-animations-1#animation-effect) are represented in the Web Animations API by the abstract [`AnimationEffect`](https://drafts.csswg.org/web-animations-1#animationeffect) interface.

```webidl
[Exposed=Window]
interface AnimationEffect {
    EffectTiming         getTiming();
    ComputedEffectTiming getComputedTiming();
    undefined            updateTiming(optional OptionalEffectTiming timing = {});
};
```

> **Note:** Note: In future, we may expose `any onupdate (double?     progress,
>                       double      currentIteration,
>                       Animatable? target,
>                       any         underlyingValue)` so that the animation effects can be driven apart from the timing model.

**`getTiming()`** 

Returns the specified timing properties for this [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect).

For the correspondence between the members of the returned [`EffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-effecttiming) object and properties of the [timing model](https://drafts.csswg.org/web-animations-1#timing-model), see the [`EffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-effecttiming) interface.

**`getComputedTiming()`** 

Returns the calculated timing properties for this [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect).

Although some of the attributes of the object returned by [`getTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-gettiming) and [`getComputedTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-getcomputedtiming) are common, their values can differ in the following ways:

*   [`duration`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-duration) – while [`getTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-gettiming) can return the string `auto`, [`getComputedTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-getcomputedtiming) must return a number corresponding to the calculated value of the [iteration duration](https://drafts.csswg.org/web-animations-1#iteration-duration) as defined in the description of the [`duration`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-duration) member of the [`EffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-effecttiming) interface.

    In this level of the specification, that simply means that an `auto` value is replaced by zero.

*   [`fill`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-fill) – likewise, while [`getTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-gettiming) can return the string `auto`, [`getComputedTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-getcomputedtiming) must return the specific [`FillMode`](https://drafts.csswg.org/web-animations-1#enumdef-fillmode) used for timing calculations as defined in the description of the [`fill`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-fill) member of the [`EffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-effecttiming) interface.

    In this level of the specification, that simply means that an `auto` value is replaced by the `none` [`FillMode`](https://drafts.csswg.org/web-animations-1#enumdef-fillmode).

> **Note:** Note: It is likely that other timing members could be extended in future to include `auto`-like values. When performing timing calculations, authors are encouraged to use [`getComputedTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-getcomputedtiming) where possible to avoid incompatibility should the range or type of allowed specified values be changed.

In addition to possible differences in the values returned, compared to [`getTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-gettiming), [`getComputedTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-getcomputedtiming) returns additional timing information as defined by the [`ComputedEffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-computedeffecttiming) dictionary.

**`updateTiming(*timing*)`** 

Updates the specified timing properties of this [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) by performing the procedure to [update the timing properties of an animation effect](https://drafts.csswg.org/web-animations-1#update-the-timing-properties-of-an-animation-effect) passing the [`timing`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-updatetiming-timing-timing) parameter as *input*.

**`optional [`OptionalEffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-optionaleffecttiming) timing`** 

The timing properties to update. The timing properties corresponding to any members that do not [exist](https://infra.spec.whatwg.org/#map-exists) on [`timing`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-updatetiming-timing-timing) will *not* be modified.

[`TypeError`](https://webidl.spec.whatwg.org/#exceptiondef-typeerror) 

Raised if any of the following conditions applies:

*   [`iterationStart`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterationstart) is negative;

*   [`iterations`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterations) is negative or `NaN`;

*   [`duration`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-duration) is negative, `NaN`, or a string other than `auto`; or

*   [`easing`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-easing) cannot be parsed as an [\<easing-function>](https://drafts.csswg.org/css-easing-2/#typedef-easing-function).

> **Issue:** The `remove()` method can be used to remove an effect from either its parent group or animation. Should we keep it in level 1 and define it simply as removing the animation effect from its animation? [\[Issue #2082\]](https://github.com/w3c/csswg-drafts/issues/2082)

#### The [`EffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-effecttiming) and [`OptionalEffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-optionaleffecttiming) dictionaries

The **`EffectTiming`** dictionary represents the timing properties of an [`AnimationEffect`](https://drafts.csswg.org/web-animations-1#animationeffect).

The **`OptionalEffectTiming`** dictionary is a variant of the [`EffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-effecttiming) dictionary that allows some members to not [exist](https://infra.spec.whatwg.org/#map-exists). This is used by the [`updateTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-updatetiming) method of the [`AnimationEffect`](https://drafts.csswg.org/web-animations-1#animationeffect) interface to perform a delta update to the timing properties of an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect).

```webidl
dictionary EffectTiming {
  double                             delay = 0;
  double                             endDelay = 0;
  FillMode                           fill = "auto";
  double                             iterationStart = 0.0;
  unrestricted double                iterations = 1.0;
  (unrestricted double or DOMString) duration = "auto";
  PlaybackDirection                  direction = "normal";
  DOMString                          easing = "linear";
};

dictionary OptionalEffectTiming {
  double                             delay;
  double                             endDelay;
  FillMode                           fill;
  double                             iterationStart;
  unrestricted double                iterations;
  (unrestricted double or DOMString) duration;
  PlaybackDirection                  direction;
  DOMString                          easing;
};
```

**`delay`**, of type [double](https://webidl.spec.whatwg.org/#idl-double), defaulting to `0` 

The [start delay](https://drafts.csswg.org/web-animations-1#start-delay), which represents the number of milliseconds from the [start time](https://drafts.csswg.org/web-animations-1#animation-start-time) of the associated [animation](https://drafts.csswg.org/web-animations-1#concept-animation) to the start of the [active interval](https://drafts.csswg.org/web-animations-1#active-interval).

**`endDelay`**, of type [double](https://webidl.spec.whatwg.org/#idl-double), defaulting to `0` 

The [end delay](https://drafts.csswg.org/web-animations-1#end-delay), which represents the number of milliseconds from the end of an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect)’s [active interval](https://drafts.csswg.org/web-animations-1#active-interval) until its [end time](https://drafts.csswg.org/web-animations-1#animation-effect-end-time).

**`fill`**, of type [FillMode](https://drafts.csswg.org/web-animations-1#enumdef-fillmode), defaulting to `"auto"` 

The [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode), which defines the behavior of the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) outside its [active interval](https://drafts.csswg.org/web-animations-1#active-interval).

When performing timing calculations the special string value `auto` is expanded to [none](https://drafts.csswg.org/web-animations-1#fill-mode-none).

> **Note:** Note: The `auto` value exists as a forwards-compatibility measure since future types of [animation effects](https://drafts.csswg.org/web-animations-1#animation-effect) are expected to produce a different computed [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode).

**As described in [§ 4.6.8 Fill behavior and fill modes](https://drafts.csswg.org/web-animations-1#fill-behavior), authors are discouraged from using indefinitely filling animations.**

**`iterationStart`**, of type [double](https://webidl.spec.whatwg.org/#idl-double), defaulting to `0.0` 

The [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect)’s [iteration start](https://drafts.csswg.org/web-animations-1#iteration-start) property, which is a finite real number greater than or equal to zero representing the [iteration index](https://drafts.csswg.org/web-animations-1#current-iteration-index) at which the animation effect begins and its progress through that iteration.

For example, a value of 0.5 indicates that the animation effect begins halfway through its first iteration. A value of 1.2 indicates the animation effect begins 20% of the way through its second iteration.

> **Note:** Note that the value of [`iterations`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterations) is effectively *added* to the [`iterationStart`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterationstart) such that an animation effect with an [`iterationStart`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterationstart) of "0.5" and [`iterations`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterations) of "2" will still repeat twice. However it will begin and end halfway through its [iteration interval](https://drafts.csswg.org/web-animations-1#iteration-interval).[`iterationStart`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterationstart) values greater than or equal to 1 are typically only useful in combination with an animation effect that has an [iteration composite operation](https://drafts.csswg.org/web-animations-2/#iteration-composite-operation) of accumulate or when the [current iteration index](https://drafts.csswg.org/web-animations-1#current-iteration-index) is otherwise significant.

**`iterations`**, of type [unrestricted double](https://webidl.spec.whatwg.org/#idl-unrestricted-double), defaulting to `1.0` 

The [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect)’s [iteration count](https://drafts.csswg.org/web-animations-1#iteration-count) property which is a real number greater than or equal to zero (including positive infinity) representing the number of times to the animation effect repeats.

This can be set to `+Infinity` to cause the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) to repeat forever (unless the duration of the effect is zero, in which case it will finish immediately).

**`duration`**, of type `(unrestricted double or DOMString)`, defaulting to `"auto"` 

The [iteration duration](https://drafts.csswg.org/web-animations-1#iteration-duration), which is a real number greater than or equal to zero (including positive infinity) representing the time taken to complete a single iteration of the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect).

In this level of this specification, the string value `auto` is treated as the value zero for the purpose of timing model calculations and for the result of the [`duration`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-duration) member returned from [`getComputedTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-getcomputedtiming). If the author specifies the `auto` value, user agents must, however, return `auto` for the [`duration`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-duration) member returned from [`getTiming()`](https://drafts.csswg.org/web-animations-1#dom-animationeffect-gettiming).

> **Note:** Note: This is a forwards-compatibility measure since a future level of this specification is expected to introduce group effects where the `auto` value expands to include the duration of the child effects.

**`direction`**, of type [PlaybackDirection](https://drafts.csswg.org/web-animations-1#enumdef-playbackdirection), defaulting to `"normal"` 

The [playback direction](https://drafts.csswg.org/web-animations-1#playback-direction) of the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect), which defines whether playback proceeds forwards, backwards, or alternates on each iteration.

**`easing`**, of type [DOMString](https://webidl.spec.whatwg.org/#idl-DOMString), defaulting to `"linear"` 

The [easing function](https://drafts.csswg.org/css-easing-2/#easing-function) used to scale the time to produce easing effects.

The syntax of the string is defined by the [\<easing-function>](https://drafts.csswg.org/css-easing-2/#typedef-easing-function) production \[CSS-EASING-1\].

#### The [`FillMode`](https://drafts.csswg.org/web-animations-1#enumdef-fillmode) enumeration

```webidl
enum FillMode { "none", "forwards", "backwards", "both", "auto" };
```

Represents an [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect)’s [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode).

**`none`** 

No fill. ([Fill mode](https://drafts.csswg.org/web-animations-1#fill-mode) [none](https://drafts.csswg.org/web-animations-1#fill-mode-none).)

**`forwards`** 

Fill [forwards](https://drafts.csswg.org/web-animations-1#fill-mode-forwards).

**`backwards`** 

Fill [backwards](https://drafts.csswg.org/web-animations-1#fill-mode-backwards).

**`both`** 

Fill [both](https://drafts.csswg.org/web-animations-1#fill-mode-both) backwards and forwards.

**`auto`** 

No fill. In a subsequent level of this specification, this may produce different behavior for other types of [animation effects](https://drafts.csswg.org/web-animations-1#animation-effect).

#### The [`PlaybackDirection`](https://drafts.csswg.org/web-animations-1#enumdef-playbackdirection) enumeration

```webidl
enum PlaybackDirection { "normal", "reverse", "alternate", "alternate-reverse" };
```

**`normal`** 

All iterations are played as specified.

**`reverse`** 

All iterations are played in the reverse direction from the order they are specified.

**`alternate`** 

Even iterations are played as specified, odd iterations are played in the reverse direction from the order they are specified.

**`alternate-reverse`** 

Even iterations are played in the reverse direction from the order they are specified, odd iterations are played as specified.

#### Updating the timing of an [`AnimationEffect`](https://drafts.csswg.org/web-animations-1#animationeffect)

To **update the timing properties of an animation effect**, *effect*, from an [`EffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-effecttiming) or [`OptionalEffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-optionaleffecttiming) object, *input*, perform the following steps:

1.  If the [`iterationStart`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterationstart) member of *input* [exists](https://infra.spec.whatwg.org/#map-exists) and is less than zero, [throw](https://webidl.spec.whatwg.org/#dfn-throw) a [`TypeError`](https://webidl.spec.whatwg.org/#exceptiondef-typeerror) and abort this procedure.

    > **Note:** Note: The reason for using a [`TypeError`](https://webidl.spec.whatwg.org/#exceptiondef-typeerror) rather than a [`RangeError`](https://webidl.spec.whatwg.org/#exceptiondef-rangeerror) is to mirror the behavior of WebIDL’s [\[EnforceRange\]](https://webidl.spec.whatwg.org/#EnforceRange) annotation should that annotation be able to be used with floating-point values in the future.

2.  If the [`iterations`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterations) member of *input* [exists](https://infra.spec.whatwg.org/#map-exists), and is less than zero or is the value `NaN`, [throw](https://webidl.spec.whatwg.org/#dfn-throw) a [`TypeError`](https://webidl.spec.whatwg.org/#exceptiondef-typeerror) and abort this procedure.

3.  If the [`duration`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-duration) member of *input* [exists](https://infra.spec.whatwg.org/#map-exists), and is less than zero, is the value `NaN`, or is a string other than the lowercase `auto`, [throw](https://webidl.spec.whatwg.org/#dfn-throw) a [`TypeError`](https://webidl.spec.whatwg.org/#exceptiondef-typeerror) and abort this procedure.

4.  If the [`easing`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-easing) member of *input* [exists](https://infra.spec.whatwg.org/#map-exists) but cannot be parsed using the [\<easing-function>](https://drafts.csswg.org/css-easing-2/#typedef-easing-function) production \[CSS-EASING-1\], [throw](https://webidl.spec.whatwg.org/#dfn-throw) a [`TypeError`](https://webidl.spec.whatwg.org/#exceptiondef-typeerror) and abort this procedure.

5.  Assign each member that [exists](https://infra.spec.whatwg.org/#map-exists) in *input* to the corresponding timing property of *effect* as follows:

    *   [`delay`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-delay) → [start delay](https://drafts.csswg.org/web-animations-1#start-delay)

    *   [`endDelay`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-enddelay) → [end delay](https://drafts.csswg.org/web-animations-1#end-delay)

    *   [`fill`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-fill) → [fill mode](https://drafts.csswg.org/web-animations-1#fill-mode)

    *   [`iterationStart`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterationstart) → [iteration start](https://drafts.csswg.org/web-animations-1#iteration-start)

    *   [`iterations`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-iterations) → [iteration count](https://drafts.csswg.org/web-animations-1#iteration-count)

    *   [`duration`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-duration) → [iteration duration](https://drafts.csswg.org/web-animations-1#iteration-duration)

    *   [`direction`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-direction) → [playback direction](https://drafts.csswg.org/web-animations-1#playback-direction)

    *   [`easing`](https://drafts.csswg.org/web-animations-1#dom-effecttiming-easing) → [easing function](https://drafts.csswg.org/css-easing-2/#easing-function)
6.  If *effect* is [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation), run the procedure to [update an animation’s finished state](https://drafts.csswg.org/web-animations-1#update-an-animations-finished-state) for its associated animation with the *did seek* flag set to false, and the *synchronously notify* flag set to false.

#### The `ComputedEffectTiming` dictionary

Timing properties calculated by the timing model are exposed using [`ComputedEffectTiming`](https://drafts.csswg.org/web-animations-1#dictdef-computedeffecttiming) dictionary objects.

```webidl
dictionary ComputedEffectTiming : EffectTiming {
  unrestricted double  endTime;
  unrestricted double  activeDuration;
  double?              localTime;
  double?              progress;
  unrestricted double? currentIteration;
};
```

**`endTime`**, of type [unrestricted double](https://webidl.spec.whatwg.org/#idl-unrestricted-double) 

The [end time](https://drafts.csswg.org/web-animations-1#animation-effect-end-time) of the [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) expressed in milliseconds since zero [local time](https://drafts.csswg.org/web-animations-1#local-time) (that is, since the associated [animation](https://drafts.csswg.org/web-animations-1#concept-animation)’s [start time](https://drafts.csswg.org/web-animations-1#animation-start-time) if this animation effect is [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation)). This corresponds to the end of the animation effect’s [active interval](https://drafts.csswg.org/web-animations-1#active-interval) plus any [end delay](https://drafts.csswg.org/web-animations-1#end-delay).

**`activeDuration`**, of type [unrestricted double](https://webidl.spec.whatwg.org/#idl-unrestricted-double) 

The [active duration](https://drafts.csswg.org/web-animations-1#active-duration) of this [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect).

**`localTime`**, of type [double](https://webidl.spec.whatwg.org/#idl-double), nullable 

The [local time](https://drafts.csswg.org/web-animations-1#local-time) of this [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect).

This will be `null` if this [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect) is not [associated with an animation](https://drafts.csswg.org/web-animations-1#animation-effect-associated-animation).

**`progress`**, of type [double](https://webidl.spec.whatwg.org/#idl-double), nullable 

The current [iteration progress](https://drafts.csswg.org/web-animations-1#iteration-progress) of this [animation effect](https://drafts.csswg.org/web-animations-1#animation-effect).

**`currentIteration`**, of type [unrestricted double](https://webidl.spec.whatwg.org/#idl-unrestricted-double), nullable 

The [current iteration index](https://drafts.csswg.org/web-animations-1#current-iteration-index) beginning with zero for the first iteration.

In most cases this will be a (positive) integer. However, for a zero-duration animation that repeats infinite times, the value will be positive `Infinity`.

As with [unresolved](https://drafts.csswg.org/web-animations-1#unresolved) times, an unresolved [iteration index](https://drafts.csswg.org/web-animations-1#current-iteration-index) is represented by a `null` value.

## Navigation

- Parent: `programming-interface` — Programming interface
- Prev: `the-animation-interface` — The Animation interface
- Next: `the-keyframeeffect-interface` — The KeyframeEffect interface
- Children: 9
  - `animationeffect` — AnimationEffect
  - `dom-animationeffect-gettiming` — getTiming()
  - `dom-animationeffect-getcomputedtiming` — getComputedTiming()
  - `dom-animationeffect-updatetiming` — updateTiming(timing)
  - `the-effecttiming-dictionaries` — The EffectTiming and OptionalEffectTiming dictionaries
  - `the-fillmode-enumeration` — The FillMode enumeration
  - `the-playbackdirection-enumeration` — The PlaybackDirection enumeration
  - `updating-animationeffect-timing` — Updating the timing of an AnimationEffect
  - `the-computedeffecttiming-dictionary` — The ComputedEffectTiming dictionary

## Outgoing refs (23)

`webspec-index refs WEB-ANIMATIONS-1#the-animationeffect-interface -d outgoing -l 23`

## Incoming refs (1)

- WEB-ANIMATIONS-1#contents

### Possible effects

WEB-ANIMATIONS-1#the-animationeffect-interface

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#the-animationeffect-interface" --format markdown`
