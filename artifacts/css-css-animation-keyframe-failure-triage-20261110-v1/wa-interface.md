# WEB-ANIMATIONS-1#the-keyframeeffect-interface

**The KeyframeEffect interface** (heading)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

[Keyframe effects](WEB-ANIMATIONS-1#keyframe-effect) are represented by the **`KeyframeEffect`** interface.

```webidl
[Exposed=Window]
interface KeyframeEffect : AnimationEffect {
  constructor(Element?       target,
              object?        keyframes,
              optional (unrestricted double or KeyframeEffectOptions) options = {});
  constructor(KeyframeEffect source);
  attribute Element?           target;
  attribute CSSOMString?       pseudoElement;
  attribute CompositeOperation composite;
  sequence<object> getKeyframes();
  undefined        setKeyframes(object? keyframes);
};
```

Tests

*   [effect-in-removed-iframe-crash.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/effect-in-removed-iframe-crash.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/effect-in-removed-iframe-crash.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/effect-in-removed-iframe-crash.html)

**`
  KeyframeEffect (*target*, *keyframes*, *options*)`** 

Creates a new [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) object using the following procedure:

1.  Create a new [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) object, *effect*.

2.  Set the [target element](WEB-ANIMATIONS-1#effect-target-target-element) of *effect* to *target*.

3.  Set the [target pseudo-selector](WEB-ANIMATIONS-1#effect-target-target-pseudo-selector) to the result corresponding to the first matching condition below:

    If *options* is a [`KeyframeEffectOptions`](WEB-ANIMATIONS-1#dictdef-keyframeeffectoptions) object with a [`pseudoElement`](WEB-ANIMATIONS-1#dom-keyframeeffectoptions-pseudoelement) property,

    Set the [target pseudo-selector](WEB-ANIMATIONS-1#effect-target-target-pseudo-selector) to the value of the [`pseudoElement`](WEB-ANIMATIONS-1#dom-keyframeeffectoptions-pseudoelement) property.

    When assigning this property, the error-handling defined for the [`pseudoElement`](WEB-ANIMATIONS-1#dom-keyframeeffect-pseudoelement) setter on the interface is applied. If the setter requires an exception to be thrown, this procedure must throw the same exception and abort all further steps.

    Otherwise,

    Set the [target pseudo-selector](WEB-ANIMATIONS-1#effect-target-target-pseudo-selector) to `null`.

4.  Let *timing input* be the result corresponding to the first matching condition below:

    If *options* is a [`KeyframeEffectOptions`](WEB-ANIMATIONS-1#dictdef-keyframeeffectoptions) object,

    Let *timing input* be *options*.

    Otherwise (if *options* is a `double`),

    Let *timing input* be a new [`EffectTiming`](WEB-ANIMATIONS-1#dictdef-effecttiming) object with all members set to their default values and [`duration`](WEB-ANIMATIONS-1#dom-effecttiming-duration) set to *options*.

5.  Call the procedure to [update the timing properties of an animation effect](WEB-ANIMATIONS-1#update-the-timing-properties-of-an-animation-effect) of *effect* from *timing input*.

    If that procedure causes an exception to be thrown, propagate the exception and abort this procedure.

6.  If *options* is a [`KeyframeEffectOptions`](WEB-ANIMATIONS-1#dictdef-keyframeeffectoptions) object, assign the [`composite`](WEB-ANIMATIONS-1#dom-keyframeeffect-composite) property of *effect* to the corresponding value from *options*.

    When assigning this property, the error-handling defined for the corresponding setter on the [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) interface is applied. If the setter requires an exception to be thrown for the value specified by *options*, this procedure must [throw](WEBIDL#dfn-throw) the same exception and abort all further steps.

7.  Initialize the set of [keyframes](WEB-ANIMATIONS-1#keyframe) by performing the procedure defined for [`setKeyframes()`](WEB-ANIMATIONS-1#dom-keyframeeffect-setkeyframes) passing *keyframes* as the input.

**[``Element``](DOM#element)** 

The [target element](WEB-ANIMATIONS-1#effect-target-target-element). This may be `null` for animations that do not target a specific element.

**`object? keyframes`** 

The set of [keyframes](WEB-ANIMATIONS-1#keyframe) to use. The format and processing of this argument is defined in [§ 6.6.3 Processing a keyframes argument](WEB-ANIMATIONS-1#processing-a-keyframes-argument).

**`optional [`KeyframeEffectOptions`](https://drafts.csswg.org/web-animations-1#dictdef-keyframeeffectoptions) options`** 

Either a number specifying the [iteration duration](WEB-ANIMATIONS-1#iteration-duration) of the effect, or a collection of properties specifying the timing and behavior of the effect.

Examples of the usage of this constructor are given in [§ 6.6.1 Creating a new KeyframeEffect object](WEB-ANIMATIONS-1#creating-a-new-keyframeeffect-object).

**`KeyframeEffect (source)`** 

Creates a new [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) object with the same properties as [`source`](WEB-ANIMATIONS-1#dom-keyframeeffect-keyframeeffect-source-source) using the following procedure:

1.  Create a new [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) object, *effect*.

2.  Set the following properties of *effect* using the corresponding values of *source*:

    *   [effect target](WEB-ANIMATIONS-1#keyframe-effect-effect-target),

    *   [keyframes](WEB-ANIMATIONS-1#keyframe),

    *   [composite operation](WEB-ANIMATIONS-1#composite-operation), and

    *   all specified timing properties:

        *   [start delay](WEB-ANIMATIONS-1#start-delay),

        *   [end delay](WEB-ANIMATIONS-1#end-delay),

        *   [fill mode](WEB-ANIMATIONS-1#fill-mode),

        *   [iteration start](WEB-ANIMATIONS-1#iteration-start),

        *   [iteration count](WEB-ANIMATIONS-1#iteration-count),

        *   [iteration duration](WEB-ANIMATIONS-1#iteration-duration),

        *   [playback direction](WEB-ANIMATIONS-1#playback-direction), and

        *   [easing function](CSS-EASING-2#easing-function).

    > **Note:** Note: Unlike the [`KeyframeEffect(target, keyframes, options)`](WEB-ANIMATIONS-1#dom-keyframeeffect-keyframeeffect) constructor, we do not need to re-throw exceptions since the timing properties specified on *source* can be assumed to be valid.

**[``KeyframeEffect``](WEB-ANIMATIONS-1#keyframeeffect)** 

The [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect) from which to copy the properties that define the new keyframe effect.

**`target`**, of type [Element](DOM#element), nullable 

The [target element](WEB-ANIMATIONS-1#effect-target-target-element) being animated by this object (either the [effect target](WEB-ANIMATIONS-1#keyframe-effect-effect-target) if it is an [`Element`](DOM#element) or its [originating element](SELECTORS-4#originating-element) if it is a pseudo-element). This may be `null` for animations that do not target a specific element such as an animation that produces a sound using an audio API.

**`pseudoElement`**, of type [CSSOMString](CSSOM-1#cssomstring), nullable 

The [target pseudo-selector](WEB-ANIMATIONS-1#effect-target-target-pseudo-selector). `null` if this effect has no [effect target](WEB-ANIMATIONS-1#keyframe-effect-effect-target) or if the effect target is an element (i.e. not a pseudo-element). When the effect target is a pseudo-element, this specifies the pseudo-element selector (e.g. `::before`).

On setting, sets the [target pseudo-selector](WEB-ANIMATIONS-1#effect-target-target-pseudo-selector) of the [animation effect](WEB-ANIMATIONS-1#animation-effect) to the result of **`pseudo-element parsing`** on the provided value, defined as the following:

1.  Given the value *value*, perform the following steps:

2.  If *value* is not `null` and is an [invalid](SELECTORS-4#invalid-selector) [\<pseudo-element-selector>](SELECTORS-4#typedef-pseudo-element-selector),

    1.  [Throw](WEBIDL#dfn-throw) a [`DOMException`](WEBIDL#idl-DOMException) with error name "[`SyntaxError`](WEBIDL#syntaxerror)".

    2.  Abort.

        > **Note:** Note: In effect, this means that if the result of this algorithm is used to set a variable, then that variable remains unchanged.

    > **Note:** Note: Invalid in this context follows the definition of an [invalid selector](SELECTORS-4#invalid-selector) defined in \[SELECTORS-4\] such that syntactically invalid pseudo-elements as well as pseudo-elements for which the user agent has no usable level of support are both deemed invalid.

3.  If *value* is one of the legacy Selectors Level 2 single-colon selectors (':before', ':after', ':first-letter', or ':first-line'), then return the equivalent two-colon selector (e.g. '::before').

4.  Otherwise, return *value*.

**`composite`**, of type [CompositeOperation](WEB-ANIMATIONS-1#enumdef-compositeoperation) 

The [composite operation](WEB-ANIMATIONS-1#composite-operation) used to composite this [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect) with the [effect stack](WEB-ANIMATIONS-1#effect-stack), as specified by one of the [`CompositeOperation`](WEB-ANIMATIONS-1#enumdef-compositeoperation) enumeration values.

On setting, sets the [composite operation](WEB-ANIMATIONS-1#composite-operation) property of this [animation effect](WEB-ANIMATIONS-1#animation-effect) to the provided value.

**`sequence<object> getKeyframes()`** 

Returns the keyframes that make up this effect along with their [computed keyframe offsets](WEB-ANIMATIONS-1#computed-keyframe-offsets).

*This section is non-normative*The result of this method is a sequence of objects of the following format:

```
dictionary ComputedKeyframe {
  // ... property-value pairs ...
  // i.e. DOMString propertyName
  double?                  offset = null;
  double                   computedOffset;
  DOMString                easing = "linear";
  CompositeOperationOrAuto composite = "auto";
};
```

The meaning and values of each member is as follows:

`offset` 

The [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset) of the [keyframe](WEB-ANIMATIONS-1#keyframe) specified as a number between 0.0 and 1.0 inclusive, or `null`.

This will be `null` if the [keyframe](WEB-ANIMATIONS-1#keyframe) is to be automatically spaced between adjacent keyframes.

`computedOffset` 

The [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) for this [keyframe](WEB-ANIMATIONS-1#keyframe) calculated as part of running the [compute missing keyframe offsets](WEB-ANIMATIONS-1#compute-missing-keyframe-offsets) procedure.

Unlike the `offset` member, the `computedOffset` is never `null`.

`easing` 

The [easing function](CSS-EASING-2#easing-function) used to transform the progress of time from this keyframe until the next keyframe in the series.

`composite` 

The [keyframe-specific composite operation](WEB-ANIMATIONS-1#keyframe-specific-composite-operation) used to combine the values specified in this keyframe with the [underlying value](WEB-ANIMATIONS-1#underlying-value).

This member will be [`auto`](WEB-ANIMATIONS-1#dom-compositeoperationorauto-auto) if the [composite operation](WEB-ANIMATIONS-1#composite-operation) specified on the [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect) is being used.

Since [keyframes](WEB-ANIMATIONS-1#keyframe) are represented by a partially open-ended dictionary type that is not currently able to be expressed with WebIDL, the procedure used to prepare the result of this method is defined in prose below:

1.  Let *result* be an empty sequence of objects.

2.  Let *keyframes* be one of the following:

    If this [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect) is associated with a [`CSSAnimation`](CSS-ANIMATIONS-2#cssanimation), and its [keyframes](WEB-ANIMATIONS-1#keyframe) have not been replaced by a successful call to [`setKeyframes()`](WEB-ANIMATIONS-1#dom-keyframeeffect-setkeyframes),

    the [computed keyframes](WEB-ANIMATIONS-1#computed-keyframes) for this [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect).

    Otherwise,

    the result of applying the procedure [compute missing keyframe offsets](WEB-ANIMATIONS-1#compute-missing-keyframe-offsets) to the [keyframes](WEB-ANIMATIONS-1#keyframe) for this [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect).

    > **Note:** Note: We return [computed keyframes](WEB-ANIMATIONS-1#computed-keyframes) for CSS Animations because not all keyframes specified in CSS can be represented by a dictionary.

3.  For each *keyframe* in *keyframes* perform the following steps:

    1.  Initialize a dictionary object, *output keyframe*, using the following definition:

        ```webidl
        dictionary BaseComputedKeyframe {
             double?                  offset = null;
             double                   computedOffset;
             DOMString                easing = "linear";
             CompositeOperationOrAuto composite = "auto";
        };
        ```

    2.  Set the [`offset`](WEB-ANIMATIONS-1#dom-basecomputedkeyframe-offset), [`computedOffset`](WEB-ANIMATIONS-1#dom-basecomputedkeyframe-computedoffset), [`easing`](WEB-ANIMATIONS-1#dom-basecomputedkeyframe-easing), and [`composite`](WEB-ANIMATIONS-1#dom-basecomputedkeyframe-composite) members of *output keyframe* to the respective [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset), [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets), keyframe-specific [easing function](CSS-EASING-2#easing-function), and [keyframe-specific composite operation](WEB-ANIMATIONS-1#keyframe-specific-composite-operation) values of *keyframe*.

    3.  For each animation property-value pair *declaration* in *keyframe*, perform the following steps:

        1.  Let *property name* be the result of applying the [animation property name to IDL attribute name](WEB-ANIMATIONS-1#animation-property-name-to-idl-attribute-name) algorithm to the property name of *declaration*.

        2.  Let *IDL value* be the result of serializing the property value of *declaration* by passing *declaration* to the algorithm to [serialize a CSS value](CSSOM#serialize-a-css-value) \[CSSOM\].

        3.  Let *value* be the result of [converting](WEBIDL#DOMString-to-es) *IDL value* to an ECMAScript String value.

        4.  Call the [\[\[DefineOwnProperty\]\]](http://www.ecma-international.org/ecma-262/6.0/#sec-ordinary-object-internal-methods-and-internal-slots-defineownproperty-p-desc) internal method on *output keyframe* with property name *property name*, Property Descriptor { \[\[Writable\]\]: true, \[\[Enumerable\]\]: true, \[\[Configurable\]\]: true, \[\[Value\]\]: *value* } and Boolean flag false.
    4.  Append *output keyframe* to *result*.
4.  Return *result*.

**`void setKeyframes(object? keyframes)`** 

Replaces the set of [keyframes](WEB-ANIMATIONS-1#keyframe) that make up this effect.

**`object? keyframes`** 

A series of keyframes whose format and processing is defined by [§ 6.6.3 Processing a keyframes argument](WEB-ANIMATIONS-1#processing-a-keyframes-argument).

This effect’s set of [keyframes](WEB-ANIMATIONS-1#keyframe) is replaced with the result of performing the procedure to [process a keyframes argument](WEB-ANIMATIONS-1#process-a-keyframes-argument). If that procedure throws an exception, this effect’s keyframes are not modified.

[`TypeError`](WEBIDL#exceptiondef-typeerror) 

Raised if an iterable yields a value other than `undefined`, `null`, or an object; if the keyframes are not [loosely sorted by offset](WEB-ANIMATIONS-1#loosely-sorted-by-offset); if a non-null [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset) is outside the range \[0, 1\]; or if an easing cannot be parsed as an [\<easing-function>](CSS-EASING-2#typedef-easing-function).

#### Creating a new `KeyframeEffect` object

*This section is non-normative*The [`KeyframeEffect`](WEB-ANIMATIONS-1#dom-keyframeeffect-keyframeeffect) constructor offers a number of approaches to creating new [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) objects.

At its simplest, a [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) object that changes the "left" property of `elem` to 100px over three seconds can be constructed as follows:

> **Example:** ```
> var effect = new KeyframeEffect(elem, { left: '100px' }, 3000);
> ```

The second parameter, representing the list of keyframes, may specify multiple properties. (See [§ 6.6.3 Processing a keyframes argument](WEB-ANIMATIONS-1#processing-a-keyframes-argument).)

> **Example:** ```
> // Specify multiple properties at once
> var effectA = new KeyframeEffect(elem, { left: '100px', top: '300px' }, 3000);
>
> // Specify multiple keyframes
> var effectB = new KeyframeEffect(elem, [ { left: '100px' }, { left: '300px' } ], 3000);
> ```

The third parameter, representing the animation’s timing, may simply be a number representing the [iteration duration](WEB-ANIMATIONS-1#iteration-duration) in milliseconds as above, or, to specify further timing properties such as the [start delay](WEB-ANIMATIONS-1#start-delay), an [`EffectTiming`](WEB-ANIMATIONS-1#dictdef-effecttiming) object can be used, as follows:

> **Example:** ```
> var effect =
>   new KeyframeEffect(elem, { left: '100px' }, { duration: 3000, delay: 2000 });
> ```

If the duration is not specified, a value of zero is used. It is possible to create an animation that simply sets a property without any interpolation as follows:

> **Example:** ```
> var effect =
>   new KeyframeEffect(elem, { visibility: 'hidden' }, { fill: 'forwards' });
> ```

As described in [§ 4.6.8 Fill behavior and fill modes](WEB-ANIMATIONS-1#fill-behavior) however, using indefinitely filling animations in this way is discouraged.

Having created a [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect), it can be played by adding it to an [`Animation`](WEB-ANIMATIONS-1#animation) and then playing that animation. For simple effects, however, the [`Element.animate`](WEB-ANIMATIONS-1#extensions-to-the-element-interface) shortcut is more convenient since it performs these steps automatically. For example,

> **Example:** ```
> elem.animate({ left: '100px' }, 3000);
> ```

#### Property names and IDL names

The **animation property name to IDL attribute name** algorithm for *property* is as follows:

1.  If *property* follows the [\<custom-property-name>](CSS-VARIABLES-2#typedef-custom-property-name) production, return *property*.

2.  If *property* refers to the CSS [float](CSS2#propdef-float) property, return the string "cssFloat".

3.  If *property* refers to the CSS [offset](MOTION-1#propdef-offset) property, return the string "cssOffset".

4.  Otherwise, return the result of applying the [CSS property to IDL attribute](CSSOM#css-property-to-idl-attribute) algorithm \[CSSOM\] to *property*.

The **IDL attribute name to animation property name** algorithm for *attribute* is as follows:

1.  If *attribute* conforms to the [\<custom-property-name>](CSS-VARIABLES-2#typedef-custom-property-name) production, return *attribute*.

2.  If *attribute* is the string "cssFloat", then return an animation property representing the CSS [float](CSS2#propdef-float) property.

3.  If *attribute* is the string "cssOffset", then return an animation property representing the CSS [offset](MOTION-1#propdef-offset) property.

4.  Otherwise, return the result of applying the [IDL attribute to CSS property](CSSOM#idl-attribute-to-css-property) algorithm \[CSSOM\] to *attribute*.

#### Processing a `keyframes` argument

*This section is non-normative*The following methods all accept a set of keyframes as an argument:

*   the [`KeyframeEffect(target, keyframes, options)`](WEB-ANIMATIONS-1#dom-keyframeeffect-keyframeeffect) constructor,

*   the [`setKeyframes()`](WEB-ANIMATIONS-1#dom-keyframeeffect-setkeyframes) method on the [`KeyframeEffect`](WEB-ANIMATIONS-1#keyframeeffect) interface,

*   the [`animate()`](WEB-ANIMATIONS-1#dom-animatable-animate) method of the [`Animatable`](WEB-ANIMATIONS-1#animatable) interface mixin.

This argument can be specified in the one of two forms as illustrated below:

> **Example:** ```
> // The following two expressions produce the same result:
> elem.animate([ { color: 'blue' },
>                { color: 'green' },
>                { color: 'red' },
>                { color: 'yellow' } ], 2000);
> elem.animate({ color: [ 'blue', 'green', 'red', 'yellow' ] }, 2000);
>
> // Likewise, for a multi-property animation, the following two
> // expressions are equivalent:
> elem.animate([ { color: 'blue', left: '0px' },
>                { color: 'green', left: '-20px' },
>                { color: 'red', left: '100px' },
>                { color: 'yellow', left: '50px'} ], 2000);
> elem.animate({ color: [ 'blue', 'green', 'red', 'yellow' ],
>                left: [ '0px', '-20px', '100px', '50px' ] }, 2000);
>
> // Incidentally, the following three expressions are all equivalent:
> elem.animate([ { color: 'red' } ], 1000);
> elem.animate({ color: [ 'red' ] }, 1000);
> elem.animate({ color: 'red' }, 1000);
> ```

The first form (the array-form) consists of an array of keyframes where each keyframe may specify at most one value per animation property. The second form (the object-form) consists of an object where each animation property may specify a single animation value or an array of animation values.

The first array-form is the canonical form, and is the form returned by the [`getKeyframes()`](WEB-ANIMATIONS-1#dom-keyframeeffect-getkeyframes) method.

[Keyframe offsets](WEB-ANIMATIONS-1#keyframe-offset) can be specified using either form as illustrated below:

> **Example:** ```
> // The keyframes without offsets will automatically have offsets computed
> // as 0 for the first keyframe, 0.65 for the middle keyframe, and 1 for the
> // final keyframe.
> elem.animate([ { color: 'blue' },
>                { color: 'green', offset: 0.5 },
>                { color: 'red' },
>                { color: 'yellow', offset: 0.8 },
>                { color: 'pink' } ], 2000);
>
> // The following produces the same result. Note that it is not necessary to
> // specify the last value: it will automatically be treated as 'null' and then
> // the automatic assignment will apply as with the previous case.
> elem.animate({ color: [ 'blue', 'green', 'red', 'yellow', 'pink' ],
>                offset: [ null, 0.5, null, 0.8 ] }, 2000);
> ```

Likewise [easing functions](CSS-EASING-2#easing-function) and [keyframe-specific composite operations](WEB-ANIMATIONS-1#keyframe-specific-composite-operation) may be specified in either form. The array-form allows specifying different values for each [keyframe](WEB-ANIMATIONS-1#keyframe) whilst for the object-form, the list of values will be repeated as needed until each keyframe has been assigned a value.

> **Example:** ```
> // Since easing functions apply _between_ keyframes, even if we specify a
> // an easing function on the last keyframe it will be ignored.
> elem.animate([ { color: 'blue', easing: 'ease-in' },
>                { color: 'green', easing: 'ease-out' },
>                { color: 'yellow' } ], 2000);
>
> // The following produces the same result.
> elem.animate({ color: [ 'blue', 'green', 'yellow' ],
>                easing: [ 'ease-in', 'ease-out' ] }, 2000);
>
> // The repeating behavior makes assigning the same value to all keyframes
> // simple:
> elem.animate({ color: [ 'blue', 'green', 'yellow' ],
>                easing: 'ease-in-out' }, 2000);
> ```

Note that the `easing` property in either form sets the *keyframe-specific [easing function](CSS-EASING-2#easing-function)*. This is independent from the [easing function](CSS-EASING-2#easing-function) that applies to the entire [iteration duration](WEB-ANIMATIONS-1#iteration-duration) of the [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect) as specified using a [`KeyframeEffectOptions`](WEB-ANIMATIONS-1#dictdef-keyframeeffectoptions) object (or [`KeyframeAnimationOptions`](WEB-ANIMATIONS-1#dictdef-keyframeanimationoptions) object when using the [`animate()`](WEB-ANIMATIONS-1#dom-animatable-animate) method of the [`Animatable`](WEB-ANIMATIONS-1#animatable) interface mixin).

In the following example, the two statements produce different results.

> **Example:** ```
> // Here, 'ease-in-out' is applied between each color value.
> elem.animate({ color: [ 'blue', 'green', 'yellow' ],
>                easing: 'ease-in-out' }, 2000);
>
> // However, in this case, 'ease-in-out' is applied across the whole span
> // of the animation, that is from 'blue' to 'yellow'.
> elem.animate({ color: [ 'blue', 'green', 'yellow' ] },
>              { duration: 2000, easing: 'ease-in-out' });
> ```

The type of the `keyframes` argument cannot be expressed in WebIDL since it relies on a partially-open dictionary type.

Conceptually, the type of this argument is equivalent to the following WebIDL-like definition:

```
dictionary Keyframe {
  // ... property-value pairs ...
  // i.e. DOMString propertyName
  double?                   offset = null;
  DOMString                 easing = "linear";
  CompositeOperationOrAuto  composite = "auto";
};

dictionary PropertyIndexedKeyframes {
  // ... property-value and property-valuelist pairs ...
  // i.e. (DOMString or sequence<DOMString>) propertyName
  (double? or sequence<double?>)                         offset = [];
  (DOMString or sequence<DOMString>)                     easing = [];
  (CompositeOperationOrAuto or sequence<CompositeOperationOrAuto>) composite = [];
};

typedef (sequence<Keyframe?> or PropertyIndexedKeyframes) KeyframeArgument;
```

The meaning and allowed values of each argument is as follows:

`offset` 

The [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset) of the [keyframe](WEB-ANIMATIONS-1#keyframe) specified as a number between 0.0 and 1.0 inclusive or `null`.

A `null` value indicates that the [keyframe](WEB-ANIMATIONS-1#keyframe) should be automatically spaced between adjacent keyframes.

Specifying an offset outside the range \[0.0, 1.0\] will cause a [`TypeError`](WEBIDL#exceptiondef-typeerror) to be thrown.

Keyframes that specify an offset must be provided in increasing order of offset. Adjacent and equal offsets, however, are permitted.

`easing` 

The [easing function](CSS-EASING-2#easing-function) used to transform the progress of time from this keyframe until the next keyframe in the series.

The syntax and error-handling associated with parsing this string is identical to that defined for the [`easing`](WEB-ANIMATIONS-1#dom-effecttiming-easing) attribute of the [`EffectTiming`](WEB-ANIMATIONS-1#dictdef-effecttiming) interface.

`composite` 

The [keyframe-specific composite operation](WEB-ANIMATIONS-1#keyframe-specific-composite-operation) used to combine the values specified in this keyframe with the [underlying value](WEB-ANIMATIONS-1#underlying-value).

If [`auto`](WEB-ANIMATIONS-1#dom-compositeoperationorauto-auto), the [composite operation](WEB-ANIMATIONS-1#composite-operation) specified on the [keyframe effect](WEB-ANIMATIONS-1#keyframe-effect) will be used.

Since this type cannot be expressed in WebIDL, its processing is defined in prose following.

For each method that takes a `keyframes` argument, the procedure to [process a keyframes argument](WEB-ANIMATIONS-1#process-a-keyframes-argument) is run on the input and the result of that procedure is retained.

Tests

*   [keyframe-exceptions.html](https://wpt.fyi/results/web-animations/animation-model/keyframe-effects/keyframe-exceptions.html) [(live test)](http://wpt.live/web-animations/animation-model/keyframe-effects/keyframe-exceptions.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/web-animations/animation-model/keyframe-effects/keyframe-exceptions.html)

First we define two supporting definitions:

The instruction **check the completion record** of *result*, where *result* is a [completion record](http://www.ecma-international.org/ecma-262/6.0/#sec-completion-record-specification-type) from calling an ECMAScript operation, is equivalent to the following steps:

1.  If *result* is an [abrupt completion](http://www.ecma-international.org/ecma-262/6.0/#sec-completion-record-specification-type), [throw](WEBIDL#dfn-throw) the exception contained in the \[\[value\]\] field of *result* and abort the procedure.

    > **Issue:** What should we do if the \[\[type\]\] is break, continue, or return? Can it be?

2.  Replace *result* with the value contained in the \[\[value\]\] field of *result*.

The procedure to **process a keyframe-like object** takes two arguments:

*   an ECMAScript object, `null`, or `undefined`, *keyframe input*, and

*   an *allow lists* boolean flag

and returns a map from either property names to DOMString values if *allow lists* is false, or from property names to sequences of DOMString values otherwise, using the following procedure:

1.  Run the procedure to [convert an ECMAScript value to a dictionary type](WEBIDL#es-to-dictionary) \[WEBIDL\] with *keyframe input* as the ECMAScript value, and the dictionary type depending on the value of the *allow lists* flag as follows:

    If *allow lists* is true,

    Use the following dictionary type:

    ```webidl
    dictionary BasePropertyIndexedKeyframe {
      (double? or sequence<double?>)                         offset = [];
      (DOMString or sequence<DOMString>)                     easing = [];
      (CompositeOperationOrAuto or sequence<CompositeOperationOrAuto>) composite = [];
    };
    ```

    Otherwise,

    Use the following dictionary type:

    ```webidl
    dictionary BaseKeyframe {
      double?                  offset = null;
      DOMString                easing = "linear";
      CompositeOperationOrAuto composite = "auto";
    };
    ```

    Store the result of this procedure as *keyframe output*.

2.  If *keyframe input* is `null` or `undefined`, return *keyframe output*.

3.  Build up a list of *animatable properties* as follows:

    1.  Let *animatable properties* be a list of property names (including shorthand properties that have longhand sub-properties that are animatable) that can be animated by the UA.

    2.  Convert each property name in *animatable properties* to the equivalent IDL attribute by applying the [animation property name to IDL attribute name](WEB-ANIMATIONS-1#animation-property-name-to-idl-attribute-name) algorithm.
4.  Let *input properties* be the result of calling the [EnumerableOwnNames](http://www.ecma-international.org/ecma-262/6.0/#sec-enumerableownnames) operation with *keyframe input* as the object.

5.  Make up a new list *animation properties* that consists of all of the properties that are in *both* *input properties* and *animatable properties*, *or* which are in *input properties* and conform to the [\<custom-property-name>](CSS-VARIABLES-2#typedef-custom-property-name) production.

6.  Sort *animation properties* in ascending order by the Unicode codepoints that define each property name.

7.  For each *property name* in *animation properties*:

    1.  Let *raw value* be the result of calling the [\[\[Get\]\]](http://www.ecma-international.org/ecma-262/6.0/#sec-ordinary-object-internal-methods-and-internal-slots-get-p-receiver) internal method on *keyframe input*, with *property name* as the property key and *keyframe input* as the receiver.

    2.  [Check the completion record](WEB-ANIMATIONS-1#check-the-completion-record) of *raw value*.

    3.  Convert *raw value* to a DOMString or to a sequence of DOMStrings *property values* as follows:

        If *allow lists* is true,

        Let *property values* be the result of converting *raw value* to IDL type `(DOMString or sequence<DOMString>)` using the [procedures defined for converting an ECMAScript value to an IDL value](WEBIDL#dfn-convert-ecmascript-to-idl-value) \[WEBIDL\].

        If *property values* is a single DOMString, replace *property values* with a sequence of DOMStrings with the original value of *property values* as the only element.

        Otherwise,

        Let *property values* be the result of converting *raw value* to a DOMString using the [procedure for converting an ECMAScript value to a DOMString](WEBIDL#es-to-DOMString) \[WEBIDL\].

    4.  Calculate the *normalized property name* as the result of applying the [IDL attribute name to animation property name](WEB-ANIMATIONS-1#idl-attribute-name-to-animation-property-name) algorithm to *property name*.

    5.  Add a property to *keyframe output* with *normalized property name* as the property name, and *property values* as the property value.
8.  Return *keyframe output*.

The procedure to **process a keyframes argument** takes a [nullable](WEBIDL#dfn-nullable-type) ECMAScript object, *object*, as input, and returns a sequence of keyframes using the following procedure:

1.  If *object* is `null`, return an empty sequence of keyframes.

2.  Let *processed keyframes* be an empty sequence of [keyframes](WEB-ANIMATIONS-1#keyframe).

3.  Let *method* be the result of [GetMethod](http://www.ecma-international.org/ecma-262/6.0/#sec-getmethod)(*object*, [@@iterator](http://www.ecma-international.org/ecma-262/6.0/#sec-well-known-symbols)).

4.  [Check the completion record](WEB-ANIMATIONS-1#check-the-completion-record) of *method*.

5.  Perform the steps corresponding to the first matching condition below:

    If *method* is not undefined,

    1.  Let *iter* be [GetIterator](http://www.ecma-international.org/ecma-262/6.0/#sec-getiterator)(*object*, *method*).

    2.  [Check the completion record](WEB-ANIMATIONS-1#check-the-completion-record) of *iter*.

    3.  Repeat:

        1.  Let *next* be [IteratorStep](http://www.ecma-international.org/ecma-262/6.0/#sec-iteratorstep)(*iter*).

        2.  [Check the completion record](WEB-ANIMATIONS-1#check-the-completion-record) of *next*.

        3.  If *next* is false abort this loop.

        4.  Let *nextItem* be [IteratorValue](http://www.ecma-international.org/ecma-262/6.0/#sec-iteratorvalue)(next).

        5.  [Check the completion record](WEB-ANIMATIONS-1#check-the-completion-record) of *nextItem*.

        6.  If [Type](http://www.ecma-international.org/ecma-262/6.0/#sec-ecmascript-data-types-and-values)(*nextItem*) is not `Undefined`, `Null` or `Object`, then throw a [`TypeError`](WEBIDL#exceptiondef-typeerror) and abort these steps.

        7.  Append to *processed keyframes* the result of running the procedure to [process a keyframe-like object](WEB-ANIMATIONS-1#process-a-keyframe-like-object) passing *nextItem* as the *keyframe input* with the *allow lists* flag set to false.

    Otherwise,

    1.   Let *property-indexed keyframe* be the result of running the procedure to [process a keyframe-like object](WEB-ANIMATIONS-1#process-a-keyframe-like-object) passing *object* as the *keyframe input* with the *allow lists* flag set to true.

    2.   For each member, *m*, in *property-indexed keyframe*, perform the following steps:

         1.  Let *property name* be the key for *m*.

         2.  If *property name* is "composite", "easing", or "offset", skip the remaining steps in this loop and continue from the next member in *property-indexed keyframe* after *m*.

         3.  Let *property values* be the value for *m*.

         4.  Let *property keyframes* be an empty sequence of [keyframes](WEB-ANIMATIONS-1#keyframe).

         5.  For each value, *v*, in *property values*, perform the following steps:

             1.  Let *k* be a new [keyframe](WEB-ANIMATIONS-1#keyframe) with a `null` [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset).

             2.  Add the property-value pair, *property name* → *v*, to *k*.

             3.  Append *k* to *property keyframes*.
         6.  Apply the procedure to [compute missing keyframe offsets](WEB-ANIMATIONS-1#compute-missing-keyframe-offsets) to *property keyframes*.

         7.  Add [keyframes](WEB-ANIMATIONS-1#keyframe) in *property keyframes* to *processed keyframes*.
    3.   Sort *processed keyframes* by the [computed keyframe offset](WEB-ANIMATIONS-1#computed-keyframe-offsets) of each [keyframe](WEB-ANIMATIONS-1#keyframe) in increasing order.

    4.   Merge adjacent [keyframes](WEB-ANIMATIONS-1#keyframe) in *processed keyframes* when they have equal [computed keyframe offsets](WEB-ANIMATIONS-1#computed-keyframe-offsets).

    5.   Let *offsets* be a sequence of [nullable](WEBIDL#dfn-nullable-type) `double` values assigned based on the type of the `offset` member of the *property-indexed keyframe* as follows:

         `sequence<double?>`,

         The value of `offset` as-is.

         `double?`,

         A sequence of length one with the value of `offset` as its single item, i.e. « `offset` »,

    6.   Assign each value in *offsets* to the [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset) of the [keyframe](WEB-ANIMATIONS-1#keyframe) with the corresponding position in *processed keyframes* until the end of either sequence is reached.

    7.   Let *easings* be a sequence of [`DOMString`](WEBIDL#idl-DOMString) values assigned based on the type of the `easing` member of the *property-indexed keyframe* as follows:

         `sequence<DOMString>`,

         The value of `easing` as-is.

         `DOMString`,

         A sequence of length one with the value of `easing` as its single item, i.e. « `easing` »,

    8.   If *easings* is an empty sequence, let it be a sequence of length one containing the single value "linear", i.e. « "linear" ».

    9.   If *easings* has fewer items than *processed keyframes*, repeat the elements in *easings* successively starting from the beginning of the list until *easings* has as many items as *processed keyframes*.

         > **Example:** For example, if *processed keyframes* has five items, and *easings* is the sequence « "ease-in", "ease-out" », *easings* would be repeated to become « "ease-in", "ease-out", "ease-in", "ease-out", "ease-in" ».

    10.  If *easings* has more items than *processed keyframes*, store the excess items as *unused easings*.

    11.  Assign each value in *easings* to a property named `easing` on the [keyframe](WEB-ANIMATIONS-1#keyframe) with the corresponding position in *processed keyframes* until the end of *processed keyframes* is reached.

    12.  If the `composite` member of the *property-indexed keyframe* is *not* an empty sequence:

         1.  Let *composite modes* be a sequence of [`CompositeOperationOrAuto`](WEB-ANIMATIONS-1#enumdef-compositeoperationorauto) values assigned from the `composite` member of *property-indexed keyframe*. If that member is a single [`CompositeOperationOrAuto`](WEB-ANIMATIONS-1#enumdef-compositeoperationorauto) value operation, let *composite modes* be a sequence of length one, with the value of the `composite` as its single item.

         2.  As with *easings*, if *composite modes* has fewer items than *processed keyframes*, repeat the elements in *composite modes* successively starting from the beginning of the list until *composite modes* has as many items as *processed keyframes*.

         3.  Assign each value in *composite modes* that is not [`auto`](WEB-ANIMATIONS-1#dom-compositeoperationorauto-auto) to the [keyframe-specific composite operation](WEB-ANIMATIONS-1#keyframe-specific-composite-operation) on the [keyframe](WEB-ANIMATIONS-1#keyframe) with the corresponding position in *processed keyframes* until the end of *processed keyframes* is reached.

6.  If *processed keyframes* is not [loosely sorted by offset](WEB-ANIMATIONS-1#loosely-sorted-by-offset), [throw](WEBIDL#dfn-throw) a [`TypeError`](WEBIDL#exceptiondef-typeerror) and abort these steps.

7.  If there exist any [keyframe](WEB-ANIMATIONS-1#keyframe) in *processed keyframes* whose [keyframe offset](WEB-ANIMATIONS-1#keyframe-offset) is non-null and less than zero or greater than one, [throw](WEBIDL#dfn-throw) a [`TypeError`](WEBIDL#exceptiondef-typeerror) and abort these steps.

8.  For each *frame* in *processed keyframes*, perform the following steps:

    1.  For each property-value pair in *frame*, parse the property value using the syntax specified for that property.

        If the property value is invalid according to the syntax for the property, discard the property-value pair. User agents that provide support for diagnosing errors in content SHOULD produce an appropriate warning highlighting the invalid property value.

    2.  Let the [easing function](CSS-EASING-2#easing-function) of *frame* be the result of parsing the `easing` property on *frame* using the CSS syntax defined for the [`easing`](WEB-ANIMATIONS-1#dom-effecttiming-easing) member of the [`EffectTiming`](WEB-ANIMATIONS-1#dictdef-effecttiming) dictionary.

        If parsing the `easing` property fails, [throw](WEBIDL#dfn-throw) a [`TypeError`](WEBIDL#exceptiondef-typeerror) and abort this procedure.

        > **Note:** Note: Using the CSS parser in both of the above steps implies that CSS comments and escaping are allowed, but are not retained when the value is successfully parsed.

        > **Note:** Note: In the case where the `easing` property fails to parse, it is important that the [`TypeError`](WEBIDL#exceptiondef-typeerror) is thrown *after* all reading the properties from *object* since failing to do so would be observable and will not match the behavior if partially open-ended dictionaries are later supported in WebIDL.
9.  Parse each of the values in *unused easings* using the CSS syntax defined for the [`easing`](WEB-ANIMATIONS-1#dom-effecttiming-easing) member of the [`EffectTiming`](WEB-ANIMATIONS-1#dictdef-effecttiming) dictionary, and if any of the values fail to parse, [throw](WEBIDL#dfn-throw) a [`TypeError`](WEBIDL#exceptiondef-typeerror) and abort this procedure.

    > **Note:** This final step is needed in order to provide consistent behavior such that a [`TypeError`](WEBIDL#exceptiondef-typeerror) is thrown in all of the following cases:
    >
    > ```
    > elem.animate({ easing: 'invalid' });
    > elem.animate({ easing: ['invalid'] });
    > elem.animate([{ easing: 'invalid' }]);
    > ```

#### The [`KeyframeEffectOptions`](WEB-ANIMATIONS-1#dictdef-keyframeeffectoptions) dictionary

Additional parameters may be passed to the [`KeyframeEffect(target, keyframes, options)`](WEB-ANIMATIONS-1#dom-keyframeeffect-keyframeeffect) constructor by providing a [`KeyframeEffectOptions`](WEB-ANIMATIONS-1#dictdef-keyframeeffectoptions) object.

```webidl
dictionary KeyframeEffectOptions : EffectTiming {
    CompositeOperation composite = "replace";
    CSSOMString?       pseudoElement = null;
};
```

**`composite`**, of type [CompositeOperation](WEB-ANIMATIONS-1#enumdef-compositeoperation), defaulting to `"replace"` 

The [composite operation](WEB-ANIMATIONS-1#composite-operation) used to composite this animation with the [effect stack](WEB-ANIMATIONS-1#effect-stack), as specified by one of the [`CompositeOperation`](WEB-ANIMATIONS-1#enumdef-compositeoperation) enumeration values. This is used for all [keyframes](WEB-ANIMATIONS-1#keyframe) that specify an [`auto`](WEB-ANIMATIONS-1#dom-compositeoperationorauto-auto) [keyframe-specific composite operation](WEB-ANIMATIONS-1#keyframe-specific-composite-operation).

**`pseudoElement`**, of type [CSSOMString](CSSOM-1#cssomstring), nullable, defaulting to `null` 

The [pseudo-element](SELECTORS-4#pseudo-element) selector (which must be valid or `null`) used to specify the [effect target](WEB-ANIMATIONS-1#keyframe-effect-effect-target) given the [target element](WEB-ANIMATIONS-1#effect-target-target-element).

## Navigation

- Parent: `programming-interface` — Programming interface
- Prev: `the-animationeffect-interface` — The AnimationEffect interface
- Next: `the-compositeoperation-enumeration` — The CompositeOperation and CompositeOperationOrAuto enumerations
- Children: 18
  - `keyframeeffect` — KeyframeEffect
  - `dom-keyframeeffect-keyframeeffect` — KeyframeEffect (target, keyframes, options)
  - `dom-keyframeeffect-keyframeeffect-source` — KeyframeEffect (source)
  - `dom-keyframeeffect-target` — target
  - `dom-keyframeeffect-pseudoelement` — pseudoElement
  - `dom-keyframeeffect-pseudo-element-parsing` — pseudo-element parsing
  - `dom-keyframeeffect-composite` — composite
  - `dom-keyframeeffect-getkeyframes` — sequence<object> getKeyframes()
  - `dictdef-basecomputedkeyframe` — BaseComputedKeyframe
  - `dom-basecomputedkeyframe-offset` — offset
  - `dom-basecomputedkeyframe-computedoffset` — computedOffset
  - `dom-basecomputedkeyframe-easing` — easing
  - `dom-basecomputedkeyframe-composite` — composite
  - `dom-keyframeeffect-setkeyframes` — void setKeyframes(object? keyframes)
  - `creating-a-new-keyframeeffect-object` — Creating a new KeyframeEffect object
  - `property-name-conversion` — Property names and IDL names
  - `processing-a-keyframes-argument` — Processing a keyframes argument
  - `the-keyframeeffectoptions-dictionary` — The KeyframeEffectOptions dictionary

## Outgoing refs (68)

`webspec-index refs WEB-ANIMATIONS-1#the-keyframeeffect-interface -d outgoing -l 68`

## Incoming refs (1)

- WEB-ANIMATIONS-1#contents

### Possible effects

WEB-ANIMATIONS-1#the-keyframeeffect-interface

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#the-keyframeeffect-interface" --format markdown`
