# WEB-ANIMATIONS-1#computing-property-values

**Computing property values** (heading)

**SHA**: hash:60eb4e49b329dac3a3d05a16f572436ec0fdb0551294c5e5e378531cf609d7db

## Content

To **compute a property value** given a property *property*, a value *value*, and an [`Element`](https://dom.spec.whatwg.org/#element) *element*: resolve *value* according to the “Computed Value” line of the *property*’s definition table, using the [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) of *element* as the context for resolving dependencies, and return the result.

> **Note:** Note: The [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) on *element* are not affected by this algorithm.

This algorithm implies that property values specified in keyframes can establish order dependencies. When [computing a property value](https://drafts.csswg.org/web-animations-1#compute-a-property-value), the [computed values](https://drafts.csswg.org/css-cascade-5/#computed-value) of dependencies held by *value* must be calculated *first*.

> **Example:** ```
> var animation = elem.animate([{ fontSize: '10px', width: '10em' },
>                               { fontSize: '20px', width: '20em' }], 1000);
> animation.currentTime = 500;
> console.log(getComputedStyle(elem).fontSize); // Should be 15px
> console.log(getComputedStyle(elem).width); // Should be 225px
> ```
>
> In this example, in order to [compute a property value](https://drafts.csswg.org/web-animations-1#compute-a-property-value) for `10em`, we need to know the [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) of [font-size](https://drafts.csswg.org/css-fonts-4/#propdef-font-size) on the [target element](https://drafts.csswg.org/web-animations-1#effect-target-target-element), which in turn is determined by the [effect value](https://drafts.csswg.org/web-animations-1#effect-value) for font-size, which in turn depends on computing property values for font-size. Hence, computing property values are subject to ordering constraints.

## Navigation

- Parent: `keyframe-effects` — Keyframe effects
- Prev: `keyframes-section` — Keyframes
- Next: `calculating-computed-keyframes` — Calculating computed keyframes
- Children: 1
  - `compute-a-property-value` — compute a property value

## Incoming refs (2)

- WEB-ANIMATIONS-1#calculating-computed-keyframes
- WEB-ANIMATIONS-1#contents
