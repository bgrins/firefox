# CSS-ANIMATIONS-2#keyframes

**Assembling Keyframes** (heading)

**SHA**: hash:2f3a65bc90db82e56cc0b26890a026af8c02f356e10e4bfd03e024536a243e5c

## Content

### Declaring Keyframes: the [@keyframes](https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes) rule

See [CSS Animations 1 § 3 Declaring Keyframes](https://drafts.csswg.org/css-animations-1/#keyframes).

### Processing Keyframes

For each animation effect defined by the *N*th item in the [coordinated value list](https://drafts.csswg.org/css-values-4/#coordinated-value-list) of the animation-\* properties on target (pseudo-)element *element*, its associated [keyframes](https://drafts.csswg.org/web-animations-1/#keyframe) are generated as follows:

1.  **Set Defaults:**

    *   Let *default timing function* be the corresponding [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of [animation-timing-function](https://drafts.csswg.org/css-animations-1/#propdef-animation-timing-function) on *element*.

    *   Let *default composite* be the corresponding [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of [animation-composition](https://drafts.csswg.org/css-animations-2#propdef-animation-composition) on *element*.

    *   Let *keyframes* be an empty sequence of [keyframe](https://drafts.csswg.org/web-animations-1/#keyframe) objects, each possessing a *keyframe offset*, *keyframe timing function*, *keyframe composite*, and *keyframe values*.

    *   Let *animated properties* be an empty set of CSS [property names](https://drafts.csswg.org/cssom-1/#css-declaration-property-name).
2.  **Collect Declared Keyframes:**

    1.  Find the last [@keyframes](https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes) at-rule in document order with [\<keyframes-name>](https://drafts.csswg.org/css-animations-1/#typedef-keyframes-name) matching the corresponding [animation-name](https://drafts.csswg.org/css-animations-1/#propdef-animation-name) value *name*.

        If there is no [@keyframes](https://drafts.csswg.org/css-animations-1/#at-ruledef-keyframes) at-rule with [\<keyframes-name>](https://drafts.csswg.org/css-animations-1/#typedef-keyframes-name) matching *name* (or if *name* is [none](https://drafts.csswg.org/css-animations-1/#valdef-animation-name-none)), abort this procedure. In this case no animation is generated, and any existing animation matching *name* is canceled.

    2.  Group together all [\<keyframe-block>](https://drafts.csswg.org/css-animations-1/#typedef-keyframe-block) declarations that share the same [specified](https://drafts.csswg.org/css-cascade-5/#specified-value) [\<keyframe-selector>](https://drafts.csswg.org/css-animations-1/#typedef-keyframe-selector) (treating from as 0% and to as 100%), last declared [animation-timing-function](https://drafts.csswg.org/css-animations-1/#propdef-animation-timing-function) [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) (defaulting to *default timing function* if there is no such declaration), and last declared [animation-composition](https://drafts.csswg.org/css-animations-2#propdef-animation-composition) computed value (defaulting to *default composite* if there is no such declaration).

    3.  For each such group of matching [\<keyframe-block>](https://drafts.csswg.org/css-animations-1/#typedef-keyframe-block) declarations, ordered by their earliest \<keyframe-block> in the sorted order:

        1.  [Cascade](https://drafts.csswg.org/css-cascade-6/#cascade) together all of its [declaration blocks](https://www.w3.org/TR/CSS2/syndata.html#x14) such that for each CSS property (except those that are “not animatable”, which must be ignored) the last declaration among all its [\<keyframe-block>](https://drafts.csswg.org/css-animations-1/#typedef-keyframe-block) declarations takes precedence. \[CSS-CASCADE-4\]

            > **Note:** Note: The [cascade](https://drafts.csswg.org/css-cascade-6/#cascade) will expand [shorthand properties](https://drafts.csswg.org/css-cascade-5/#shorthand-property) into their [sub-properties](https://drafts.csswg.org/css-cascade-5/#longhand) and map together corresponding property pairs in each [logical property group](https://drafts.csswg.org/css-logical-1/#logical-property-group) according to the *element*’s [computed](https://drafts.csswg.org/css-cascade-5/#computed-value) [writing mode](https://drafts.csswg.org/css-writing-modes-4/#writing-mode).

        2.  Append to *keyframes* a new empty [keyframe](https://drafts.csswg.org/web-animations-1/#keyframe) with the group’s *keyframe offset*, *keyframe timing function*, and *keyframe composite*. Give its *keyframe values* the set of [declared values](https://drafts.csswg.org/css-cascade-5/#declared-value) resulting from this cascade.

        3.  Add each [property name](https://drafts.csswg.org/cssom-1/#css-declaration-property-name) that was added to its [`cssRules`](https://drafts.csswg.org/css-animations-1/#dom-csskeyframesrule-cssrules) to *animated properties*.
3.  **Generate Initial and Final Frames:**

    1.  Find or create the *initial keyframe*, a [keyframe](https://drafts.csswg.org/web-animations-1/#keyframe) with a *keyframe offset* of 0%, *default timing function* as its *keyframe timing function*, and *default composite* as its *keyframe composite*.

    2.  For any property in *animated properties* that is not otherwise present in a keyframe with an offset of 0% or one that would be positioned earlier in the [used keyframe order](https://drafts.csswg.org/css-animations-2#used-keyframe-order), add the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of that property on *element* to *initial keyframe*’s *keyframe values*.

    3.  If *initial keyframe*’s *keyframe values* is not empty, prepend *initial keyframe* to *keyframes*.

    4.  Repeat for *final keyframe*, using an offset of 100%, considering keyframes positioned *later* in the [used keyframe order](https://drafts.csswg.org/css-animations-2#used-keyframe-order), and *appending* to *keyframes*.
4.  **Sort Frames:**

    *   The **specified order** of *keyframes* is the order resulting from the steps above, i.e. document order with duplicate keyframes collapsed to the earliest position.

    *   The **computed order** of *keyframes*—​which is the order returned by [`getKeyframes()`](https://drafts.csswg.org/web-animations-1/#dom-keyframeeffect-getkeyframes)—​is found by shifting any keyframes whose offset was specified as a [\<percentage>](https://drafts.csswg.org/css-values-4/#percentage-value), from keyword, or to keyword to the front of the list (after the generated *initial keyframe*, if any), and performing a stable sort on these keyframes by their *keyframe offset*s.

    *   The **used order** of *keyframes*—​which is the order used to interpolate and compute the actual animation frames—​is found by attaching the *keyframes* onto the animation effect’s timeline assuming an [iteration count](https://drafts.csswg.org/web-animations-1/#iteration-count) of 1 and ordering them from earliest to latest, breaking ties by using the [computed keyframe order](https://drafts.csswg.org/css-animations-2#computed-keyframe-order).

    > **Issue:** Any specific requirements on sorting computed keyframes introduced by this spec should be integrated into [Web Animations § 5.3.3 Calculating computed keyframes](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes). Any specific requirements on used keyframes introduced by this spec should be integrated into [Web Animations § 5.3.4 The effect value of a keyframe effect](https://drafts.csswg.org/web-animations-1/#the-effect-value-of-a-keyframe-animation-effect). The above description of the distinction between these sets of keyframes should be moved to an informative note.

    > **Note:** Note: Although the [computed keyframe order](https://drafts.csswg.org/css-animations-2#computed-keyframe-order) sorts keyframes with [\<percentage>](https://drafts.csswg.org/css-values-4/#percentage-value) offsets, it maintains keyframes specified with a [\<timeline-range-name>](https://drafts.csswg.org/scroll-animations-1/#typedef-timeline-range-name) in their [specified keyframe order](https://drafts.csswg.org/css-animations-2#specified-keyframe-order)—​after any \<percentage> keyframes (other than a generated *final keyframe*), even if these come later in the [used keyframe order](https://drafts.csswg.org/css-animations-2#used-keyframe-order).

## Navigation

- Prev: `animations` — Animations
- Next: `animation-definition` — Declaring Animations
- Children: 2
  - `keyframe-rules` — Declaring Keyframes: the @keyframes rule
  - `keyframe-processing` — Processing Keyframes

## Incoming refs (3)

- CSS-ANIMATIONS-2#animation-timing-function
- CSS-ANIMATIONS-2#animations
- CSS-ANIMATIONS-2#contents
