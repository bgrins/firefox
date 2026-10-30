# CSS-PROPERTIES-VALUES-API-1#behavior-of-custom-properties

**Registered Custom Properties** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

A [custom property](https://www.w3.org/TR/css-variables-1/#custom-property) can become a **registered custom property**, making it act more like a UA-defined property: giving it a syntax that’s checked by the UA, an initial value, and a specific inheritance behavior. This can be done by the [@property](https://www.w3.org/TR/css-properties-values-api-1#at-ruledef-property) rule, or the [`registerProperty()`](https://www.w3.org/TR/css-properties-values-api-1#dom-css-registerproperty) JS function.

A [custom property](https://www.w3.org/TR/css-variables-1/#custom-property) is considered to be registered for a [`Document`](https://dom.spec.whatwg.org/#document) if there is a valid [@property](https://www.w3.org/TR/css-properties-values-api-1#at-ruledef-property) rule defined for its name in one of the document’s stylesheets, or its name is [contained](https://infra.spec.whatwg.org/#map-exists) in the document’s `[[[registeredPropertySet]]](https://www.w3.org/TR/css-properties-values-api-1#dom-window-registeredpropertyset-slot)` slot (that is, [`registerProperty()`](https://www.w3.org/TR/css-properties-values-api-1#dom-css-registerproperty) was called to register it).

A [registered custom property](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) acts similarly to an unregistered [custom property](https://www.w3.org/TR/css-variables-1/#custom-property), except as defined below.

### Determining the Registration

A [registered custom property](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) has a **custom property registration** that contains all the data necessary to treat it like a real property. It’s a [struct](https://infra.spec.whatwg.org/#struct) consisting of:

*   a property name (a [custom property name string](https://drafts.css-houdini.org/css-typed-om-1/#custom-property-name-string))

*   a syntax (a [syntax string](https://www.w3.org/TR/css-properties-values-api-1#syntax-string))

*   an inherit flag (a [boolean](https://infra.spec.whatwg.org/#boolean))

*   optionally, an initial value (a [string](https://infra.spec.whatwg.org/#string) which successfully [parses](https://www.w3.org/TR/css-syntax-3/#css-parse-something-according-to-a-css-grammar) according to the syntax)

If the [`Document`](https://dom.spec.whatwg.org/#document)’s `[[[registeredPropertySet]]](https://www.w3.org/TR/css-properties-values-api-1#dom-window-registeredpropertyset-slot)` slot [contains](https://infra.spec.whatwg.org/#list-contain) a record with the [custom property’s](https://www.w3.org/TR/css-variables-1/#custom-property) name, the registration is that record.

Otherwise, if the [`Document`](https://dom.spec.whatwg.org/#document)’s active stylesheets contain at least one valid [@property](https://www.w3.org/TR/css-properties-values-api-1#at-ruledef-property) rule representing a registration with the [custom property’s](https://www.w3.org/TR/css-variables-1/#custom-property) name, the last such one in document order is the registration.

Otherwise there is no registration, and the [custom property](https://www.w3.org/TR/css-variables-1/#custom-property) is *not* a [registered custom property](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property).

### Parse-Time Behavior

[Registered custom properties](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) parse exactly like unregistered [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property); almost anything is allowed. The registered syntax of the property is *not* checked at parse time.

> **Note:** Note: However, the syntax is checked at computed-value time, before substitution via [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var). See [§ 2.4 Computed Value-Time Behavior](https://www.w3.org/TR/css-properties-values-api-1#calculation-of-computed-values).

Why aren’t custom properties syntax-checked?

When parsing a page’s CSS, UAs commonly make a number of optimizations to help with both speed and memory.

One of those optimizations is that they only store the properties that will actually have an effect; they throw away invalid properties, and if you write the same property multiple times in a single declaration block, all but the last valid one will be thrown away. (This is an important part of CSS’s error-recovery and forward-compatibility behavior.)

This works fine if the syntax of a property never changes over the lifetime of a page. If a custom property is registered, however, it can change its syntax, so that a property that was previously invalid suddenly becomes valid.

The only ways to handle this are to either store every declaration, even those that were initially invalid (increasing the memory cost of pages), or to re-parse the entire page’s CSS with the new syntax rules (increasing the processing cost of registering a custom property). Neither of these are very desirable.

Further, UA-defined properties have their syntax determined by the version of the UA the user is viewing the page with; this is out of the page author’s control, which is the entire reason for CSS’s error-recovery behavior and the practice of writing multiple declarations for varying levels of support. A custom property, on the other hand, has its syntax controlled by the page author, according to whatever stylesheet or script they’ve included in the page; there’s no unpredictability to be managed. Throwing away syntax-violating custom properties would thus only be, at best, a convenience for the page author, not a necessity like for UA-defined properties.

### [Specified Value](https://www.w3.org/TR/css-cascade-5/#specified-value)-Time Behavior

Just like unregistered [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property), all [registered custom properties](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property), regardless of registered syntax, accept the [CSS-wide keywords](https://www.w3.org/TR/css-values-4/#css-wide-keywords), such as [inherit](https://www.w3.org/TR/css-cascade-5/#valdef-all-inherit) or [revert](https://www.w3.org/TR/css-cascade-5/#valdef-all-revert). Their behavior is defined in [CSS Cascading 4 § 7.3 Explicit Defaulting](https://www.w3.org/TR/css-cascade-4/#defaulting-keywords).

### [Computed Value](https://www.w3.org/TR/css-cascade-5/#computed-value)-Time Behavior

The [computed value](https://www.w3.org/TR/css-cascade-5/#computed-value) of a [registered custom property](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) is determined by the syntax of its [registration](https://www.w3.org/TR/css-properties-values-api-1#custom-property-registration).

If the [registration’s](https://www.w3.org/TR/css-properties-values-api-1#custom-property-registration) syntax is the [universal syntax definition](https://www.w3.org/TR/css-properties-values-api-1#universal-syntax-definition), the [computed value](https://www.w3.org/TR/css-cascade-5/#computed-value) is the same as for unregistered [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property) (either the specified value with variables substituted, or the [guaranteed-invalid value](https://www.w3.org/TR/css-variables-1/#guaranteed-invalid-value)).

Otherwise, attempt to [parse](https://www.w3.org/TR/css-syntax-3/#css-parse-something-according-to-a-css-grammar) the property’s value according to its registered syntax. If this fails, the declaration is [invalid at computed-value time](https://www.w3.org/TR/css-variables-1/#invalid-at-computed-value-time) and the [computed value](https://www.w3.org/TR/css-cascade-5/#computed-value) is determined accordingly. If it succeeds, the [computed value](https://www.w3.org/TR/css-cascade-5/#computed-value) depends on the specifics of the syntax:

For `"<length>"`, `"<length-percentage>"`, `"<angle>"`, `"<time>"`, `"<resolution>"`, `"<integer>"`, `"<number>"`, and `"<percentage>"` values:

*   If the specified value is a [dimension](https://www.w3.org/TR/css-values-4/#dimension) literal (such as 50em or .2s), the computed value is the same value, but with the unit converted to the corresponding [canonical unit](https://www.w3.org/TR/css-values-4/#canonical-unit) for the type of value.

*   If the specified value is any other numeric literal (such as 5 or 20%), the computed value is as specified. (In particular, percentages are never resolved against anything.)

*   If the specified value is a function that evaluates to one of those types (such as a [math function](https://www.w3.org/TR/css-values-4/#math-function)), the computed value is defined by that function.

For `"<color>"` values, the value is computed by resolving color values, per [CSS Color 4 §  14. Resolving \<color> Values](https://www.w3.org/TR/css-color-4/#resolving-color-values).

For `"<custom-ident>"`, ident, or `"*"` values, the computed value is as specified.

For `"<url>"` values, the computed value is one of the following:

*   if the URL is a relative URL, the computed value is the resolved absolute URL as described in \[css3-values\].

*   otherwise, the computed value is as specified.

URL behavior examples

> **Example:** Because URLs resolve against the base URL of the stylesheet they appear in, we can end up with multiple relative URLs that resolve against different base URLs, even though they appear in the same property.For example, suppose --url-foo and --url-bar are registered custom properties with \<url> syntax, and that we have a stylesheet at `/style/foo/foo.css`:
>
> ```
> div {
>   --url-foo: url("foo.png");
> }
> ```
>
> and another stylesheet at `/style/bar/bar.css`
>
> ```
> div {
>   --url-bar: url("bar.png");
> }
> ```
>
> and finally a document at `/index.html`:
>
> ```
> <link href="/style/foo/foo.css" rel="stylesheet" type="text/css">
> <link href="/style/bar/bar.css" rel="stylesheet" type="text/css">
> <div style="background-image: var(--url-foo), var(---url-bar);">
> </div>
> ```
>
> Here, the var(--url-foo) reference would produce a URL that resolves against `/style/foo`, and the var(--url-bar) reference would produce a URL that resolves against `/style/bar`.
>
> On the other hand, if both --url-foo and --url-bar were *un*registered, they would substitute their literal values (relative URLs) into the `/index.html` stylesheet, which would then resolve the URLs against `/index.html` instead.

For `"<image>"` values, the computed value is the [computed \<image>](https://www.w3.org/TR/css-images-4/#computed-image).

For `"<transform-function>"` and `"<transform-list>"` values, the computed value is as specified but with all lengths resolved to their computed values.

For values with [multipliers](https://www.w3.org/TR/css-properties-values-api-1#multipliers), the computed value is a list of the computed values of the base type.

For syntaxes specified with [the | combinator](https://www.w3.org/TR/css-properties-values-api-1#combinator), the computed value is given by applying the computed-value rules for the first clause that matches the value.

### Animation Behavior

> **Note:** Note: As defined by \[css3-animations\] and \[css3-transitions\], it is possible to specify animations and transitions that reference custom properties.

When referenced by animations and transitions, custom property values [interpolate](https://www.w3.org/TR/css-values-4/#interpolation) [by computed value](https://www.w3.org/TR/web-animations-1/#by-computed-value), in accordance with the type that they parsed as.

> **Note:** Note: This implies that a list of values, such as `<color>+` or `<color>#`, will interpolate as a simple list, matching up each component index-by-index, and failing if the number of components doesn’t match.

As an exception to the above rule, a value that parsed as a `<transform-list>`, a `<transform-function>`, or a `<transform-function>+` instead interpolates as per the [transform](https://www.w3.org/TR/css-transforms-1/#propdef-transform) property.

> **Note:** Note: If, for whatever reason, a custom property is defined with a syntax of `<transform-function>#`, this will thus first interpolate as a simple list, and then each list item will interpolate as a [transform](https://www.w3.org/TR/css-transforms-1/#propdef-transform) value.

> **Note:** Note: Registering (or changing the registration) of a custom property can change its computed value, which can start or interrupt a CSS transition.

### Conditional Rules

As stated in [§ 2.2 Parse-Time Behavior](https://www.w3.org/TR/css-properties-values-api-1#parsing-custom-properties), both unregistered and [registered](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property) accept (almost) all possible values at parse-time. [Registered](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property) only apply their syntax at [computed value](https://www.w3.org/TR/css-cascade-5/#computed-value) time.

So, all [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property), regardless of whether they’re [registered](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) or unregistered, will test as "true" in an [@supports](https://www.w3.org/TR/css-conditional-3/#at-ruledef-supports) rule, so long as you don’t violate the (very liberal) generic syntax for [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property).

> **Example:** For example, even if a custom property is registered with `syntax: "<color>";`, a rule like `@supports (--foo: 1em) {...}` will still evaluate as true and apply those styles, because the declaration *does* successfully parse as a valid property.

### Substitution via [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var)

Like unregistered custom properties, the value of a registered custom property can be substituted into another value with the [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) function. However, registered custom properties substitute as their [computed value](https://www.w3.org/TR/css-properties-values-api-1#calculation-of-computed-values), rather than the original token sequence used to produce that value.

Any [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) function that references a registered custom property must be replaced with an **equivalent token sequence**, which is equal to the token sequence that would have been produced by [serializing](https://www.w3.org/TR/cssom-1/#serialize-a-css-value) the computed value, and [tokenizing](https://www.w3.org/TR/css-syntax-3/#tokenization) the resulting string.

> **Example:** Suppose that --x is registered with \<length> syntax, and that '--y’is an unregistered custom property.
>
> ```
> div {
>   font-size: 10px;
>   --x: 8em;
>   --y: var(--x);
> }
> ```
>
> Because the computed value of --x (when serialized) is "80px", the computed value of --y is a [\<dimension-token>](https://www.w3.org/TR/css-syntax-3/#typedef-dimension-token) with a value of "80" and unit "px".

#### Fallbacks In [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) References

References to registered custom properties using the [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var) function may provide a fallback. However, the fallback value must match the [syntax definition](https://www.w3.org/TR/css-properties-values-api-1#syntax-definition) of the custom property being referenced, otherwise the declaration is [invalid at computed-value time](https://www.w3.org/TR/css-variables-1/#invalid-at-computed-value-time).

> **Note:** Note: This applies regardless of whether or not the fallback is being used.

#### Dependency Cycles via Relative Units

[Registered custom properties](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) follow the same rules for dependency cycle resolution as unregistered [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property), with the following additional constraints:

For any registered custom property with a [\<length>](https://www.w3.org/TR/css-values-4/#length-value) or [\<length-percentage>](https://www.w3.org/TR/css-values-4/#typedef-length-percentage) syntax component:

*   If the property contains any of the following units: [em](https://www.w3.org/TR/css-values-4/#em), [ex](https://www.w3.org/TR/css-values-4/#ex), [cap](https://www.w3.org/TR/css-values-4/#cap), [ch](https://www.w3.org/TR/css-values-4/#ch), [ic](https://www.w3.org/TR/css-values-4/#ic), [lh](https://www.w3.org/TR/css-values-4/#lh); then add an edge between the property and the font-size of the current element.

*   If the property contains the [lh](https://www.w3.org/TR/css-values-4/#lh) unit, add an edge between the property and the line-height of the current element.

*   If the property contains any of the following units: [rem](https://www.w3.org/TR/css-values-4/#rem), [rlh](https://www.w3.org/TR/css-values-4/#rlh); then add an edge between the property and the [font-size](https://www.w3.org/TR/css-fonts-4/#propdef-font-size)' of the root element.

*   If the property contains the [rlh](https://www.w3.org/TR/css-values-4/#rlh) unit, add an edge between the property and the [line-height](https://drafts.csswg.org/css2/#propdef-line-height)' of the root element.

> **Example:** For example, given this registration:
>
> ```
> CSS.registerProperty({
>   name: "--my-font-size",
>   syntax: "<length>",
>   initialValue: "0px",
>   inherits: false
> });
> ```
>
> the following will produce a dependency cycle:
>
> ```
> div {
>   --my-font-size: 10em;
>   font-size: var(--my-font-size);
> }
> ```
>
> and font-size will behave as if the value [unset](https://www.w3.org/TR/css-cascade-5/#valdef-all-unset) was specified.

### Shadow DOM

Unlike many concepts in CSS (see [CSS Scoping 1 § 3.5 Name-Defining Constructs and Inheritance](https://drafts.csswg.org/css-scoping-1/#shadow-names)), property registrations are **not** scoped to a tree scope. All registrations, whether they appear in the outermost document or within a shadow tree, interact in a single global registration map for the [`Document`](https://dom.spec.whatwg.org/#document).

Why can’t registrations be scoped?

There are clear use-cases for property registrations to be scoped—​a component using Shadow DOM and registering some custom properties for its own internal use probably doesn’t intend for the outer page to see the registration, since the outer page doesn’t even know the component is using that property.

However, there are also reasons to not scope the registration—​custom properties are used to pipe data *into* a component, and it’s useful for the outer page to be able to set such custom properties and have them syntax-checked by the registration; similarly, concepts such as a property’s initial value don’t make much sense unless the property registration exists globally, so it applies to the property even at the document’s root.

But the above just means that registration scope might be something that should be controllable, not that it should be forced to be global.

The reason registrations must be global is because elements can exist in multiple tree scopes at the same time, with styles from each tree scope intermingling and cascading together. This applies to the [host element](https://www.w3.org/TR/css-scoping-1/#host-element0), which lives in the outer tree but is stylable from the shadow tree by the [:host](https://www.w3.org/TR/css-scoping-1/#selectordef-host0) selector, but also elements inside a shadow DOM that are targetable from the outer tree by the [::part()](https://www.w3.org/TR/css-shadow-parts-1/#selectordef-part) pseudo-element.

If registrations could be scoped to a tree scope, and a single property was registered both inside and outside, it’s not clear which registration should be applied to parse the value. Even if we tracked which tree a value came from (something we do for other tree-scoped values) and applied the corresponding registration, it’s not clear that this would give a reasonable result—​the shadow DOM might expect a property to have a particular value space, and be surprised when it receives something completely different due to the outer tree winning the cascade and applying its own registration.

When custom properties are exposed as part of a Shadow DOM-using component’s public API, this global registration behavior works as intended. If the outer page is using a custom property of the same name for different purposes, that is already a conflict that needs to be resolved, and the registration behavior does not make it worse.

If a custom property is intended for private internal usage for a component, however, it is recommended that the property be given a likely-unique name, to minimize the possibility of a clash with any other context. This can be done, for example, by including the project name, or some short random string of text, in the name of the property.

## Navigation

- Prev: `intro` — Introduction
- Next: `at-property-rule` — The @property Rule
- Children: 9
  - `registered-custom-property` — registered custom property
  - `determining-registration` — Determining the Registration
  - `parsing-custom-properties` — Parse-Time Behavior
  - `specified-value` — Specified Value-Time Behavior
  - `calculation-of-computed-values` — Computed Value-Time Behavior
  - `animation-behavior-of-custom-properties` — Animation Behavior
  - `conditional-rules` — Conditional Rules
  - `substitution` — Substitution via var()
  - `shadow-dom` — Shadow DOM

## Outgoing refs (7)

`webspec-index refs CSS-PROPERTIES-VALUES-API-1#behavior-of-custom-properties -d outgoing -l 7`

## Incoming refs (1)

- CSS-PROPERTIES-VALUES-API-1#contents
