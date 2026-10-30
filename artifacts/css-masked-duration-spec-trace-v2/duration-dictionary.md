# WEB-ANIMATIONS-1#the-effecttiming-dictionaries

**The EffectTiming and OptionalEffectTiming dictionaries** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

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

## Navigation

- Parent: `the-animationeffect-interface` — The AnimationEffect interface
- Next: `the-fillmode-enumeration` — The FillMode enumeration
- Children: 18
  - `dictdef-effecttiming` — EffectTiming
  - `dictdef-optionaleffecttiming` — OptionalEffectTiming
  - `dom-optionaleffecttiming-delay` — delay
  - `dom-optionaleffecttiming-enddelay` — endDelay
  - `dom-optionaleffecttiming-fill` — fill
  - `dom-optionaleffecttiming-iterationstart` — iterationStart
  - `dom-optionaleffecttiming-iterations` — iterations
  - `dom-optionaleffecttiming-duration` — duration
  - `dom-optionaleffecttiming-direction` — direction
  - `dom-optionaleffecttiming-easing` — easing
  - `dom-effecttiming-delay` — delay
  - `dom-effecttiming-enddelay` — endDelay
  - `dom-effecttiming-fill` — fill
  - `dom-effecttiming-iterationstart` — iterationStart
  - `dom-effecttiming-iterations` — iterations
  - `dom-effecttiming-duration` — duration
  - `dom-effecttiming-direction` — direction
  - `dom-effecttiming-easing` — easing

## Outgoing refs (39)

`webspec-index refs WEB-ANIMATIONS-1#the-effecttiming-dictionaries -d outgoing -l 39`

## Incoming refs (1)

- WEB-ANIMATIONS-1#contents

### Possible effects

WEB-ANIMATIONS-1#the-effecttiming-dictionaries

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#the-effecttiming-dictionaries" --format markdown`
