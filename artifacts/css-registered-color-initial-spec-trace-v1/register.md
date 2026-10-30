# CSS-PROPERTIES-VALUES-API-1#the-registerproperty-function

**The registerProperty() Function** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

The **`registerProperty(PropertyDefinition definition)`** method registers a custom property according to the configuration options provided in `definition`. When it is called, it executes the [register a custom property](CSS-PROPERTIES-VALUES-API-1#register-a-custom-property) algorithm, passing the options in its `definition` argument as arguments of the same names.

To **register a custom property** with *name* being a string, and optionally *syntax* being a string, *inherits* being a boolean, and *initialValue* being a string, execute these steps:

1.  Let *property set* be the value of the [current global object’s](HTML#current-global-object) [associated `Document`](HTML#concept-document-window)’s `[[[registeredPropertySet]]](https://www.w3.org/TR/css-properties-values-api-1#dom-window-registeredpropertyset-slot)` slot.

2.  If *name* is not a [custom property name string](https://drafts.css-houdini.org/css-typed-om-1/#custom-property-name-string), [throw](WEBIDL#dfn-throw) a [`SyntaxError`](WEBIDL#syntaxerror) and exit this algorithm.

    If *property set* already contains an entry with *name* as its property name (compared codepoint-wise), [throw](WEBIDL#dfn-throw) an [`InvalidModificationError`](WEBIDL#invalidmodificationerror) and exit this algorithm.

3.  Attempt to [consume a syntax definition](CSS-PROPERTIES-VALUES-API-1#consume-a-syntax-definition) from *syntax*. If it returns failure, [throw](WEBIDL#dfn-throw) a [`SyntaxError`](WEBIDL#syntaxerror). Otherwise, let *syntax definition* be the returned [syntax definition](CSS-PROPERTIES-VALUES-API-1#syntax-definition).

4.  If *syntax definition* is the [universal syntax definition](CSS-PROPERTIES-VALUES-API-1#universal-syntax-definition), and *initialValue* is not present, let *parsed initial value* be empty. This must be treated identically to the "default" initial value of custom properties, as defined in \[css-variables\]. Skip to the next step of this algorithm.

    Otherwise, if *syntax definition* is the [universal syntax definition](CSS-PROPERTIES-VALUES-API-1#universal-syntax-definition), [parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) *initialValue* as a [\<declaration-value>](CSS-SYNTAX-3#typedef-declaration-value). If this fails, [throw](WEBIDL#dfn-throw) a [`SyntaxError`](WEBIDL#syntaxerror) and exit this algorithm. Otherwise, let *parsed initial value* be the parsed result. Skip to the next step of this algorithm.

    Otherwise, if *initialValue* is not present, [throw](WEBIDL#dfn-throw) a [`SyntaxError`](WEBIDL#syntaxerror) and exit this algorithm.

    Otherwise, [parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) [`initialValue`](CSS-PROPERTIES-VALUES-API-1#dom-propertydefinition-initialvalue) according to *syntax definition*. If this fails, [throw](WEBIDL#dfn-throw) a [`SyntaxError`](WEBIDL#syntaxerror) and exit this algorithm.

    Otherwise, let *parsed initial value* be the parsed result. If *parsed initial value* is not [computationally independent](CSS-PROPERTIES-VALUES-API-1#computationally-independent), [throw](WEBIDL#dfn-throw) a [`SyntaxError`](WEBIDL#syntaxerror) and exit this algorithm.

5.  Set *inherit flag* to the value of *inherits*.

6.  Let *registered property* be a [struct](INFRA#struct) with a property name of *name*, a syntax of *syntax definition*, an initial value of *parsed initial value*, and an inherit flag of *inherit flag*. [Append](INFRA#set-append) *registered property* to *property set*.

A property value is **computationally independent** if it can be converted into a computed value using only the value of the property on the element, and "global" information that cannot be changed by CSS.

> **Example:** For example, 5px is [computationally independent](CSS-PROPERTIES-VALUES-API-1#computationally-independent), as converting it into a computed value doesn’t change it at all. Similarly, 1in is [computationally independent](CSS-PROPERTIES-VALUES-API-1#computationally-independent), as converting it into a computed value relies only on the "global knowledge" that 1in is 96px, which can’t be altered or adjusted by anything in CSS.On the other hand, 3em is not [computationally independent](CSS-PROPERTIES-VALUES-API-1#computationally-independent), because it relies on the value of [font-size](CSS-FONTS-4#propdef-font-size) on the element (or the element’s parent). Neither is a value with a [var()](CSS-VARIABLES-1#funcdef-var) function, because it relies on the value of a [custom property](CSS-VARIABLES-1#custom-property).

When a custom property is registered with a given type, the process via which specified values for that property are turned into computed values is defined fully by the type selected, as described in [§ 2.4 Computed Value-Time Behavior](CSS-PROPERTIES-VALUES-API-1#calculation-of-computed-values).

> **Note:** Note: A way to unregister properties may be added in the future.

Registering a custom property must **not** affect the [cascade](CSS-CASCADE-6#cascade) in any way. Regardless of what syntax is specified for a registered property, at parse time it is still parsed as normal for a [custom property](CSS-VARIABLES-1#custom-property), accepting nearly anything. If the [specified value](CSS-CASCADE-5#specified-value) for a [registered custom property](CSS-PROPERTIES-VALUES-API-1#registered-custom-property) violates the registered syntax, however, the property becomes [invalid at computed-value time](CSS-VARIABLES-1#invalid-at-computed-value-time) (and thus resets to the registered initial value).

> **Example:** By default, all custom property declarations that can be parsed as a sequence of tokens are valid. Hence, the result of this stylesheet:
>
> ```
> .thing {
>   --my-color: green;
>   --my-color: url("not-a-color");
>   color: var(--my-color);
> }
> ```
>
> is to set the [color](CSS-COLOR-4#propdef-color) property of elements of class "thing" to [inherit](CSS-CASCADE-5#valdef-all-inherit). The second --my-color declaration overrides the first at parse time (both are valid), and the [var()](CSS-VARIABLES-1#funcdef-var) reference in the [color](CSS-COLOR-4#propdef-color) property is found to be [invalid at computed-value time](CSS-VARIABLES-1#invalid-at-computed-value-time) (because url("not-a-color") is not a color). At this stage of the CSS pipeline (computation time), the only available fallback is the initial value of the property, which in the case of color is [inherit](CSS-CASCADE-5#valdef-all-inherit). Although there was a valid usable value (green), this was removed during parsing because it was superseded by the URL.
>
> If we call:
>
> ```
> CSS.registerProperty({
>   name: "--my-color",
>   syntax: "<color>",
>   initialValue: "black",
>   inherits: false
> });
> ```
>
> the parsing doesn’t significantly change, regardless of whether the registration occurs before or after the stylesheet above. The only difference is that it’s the --my-color property that becomes [invalid at computed-value time](CSS-VARIABLES-1#invalid-at-computed-value-time) instead and gets set to its initial value of [black](CSS-COLOR-4#valdef-color-black); then [color](CSS-COLOR-4#propdef-color) is validly set to [black](CSS-COLOR-4#valdef-color-black), rather than being [invalid at computed-value time](CSS-VARIABLES-1#invalid-at-computed-value-time) and becoming [inherit](CSS-CASCADE-5#valdef-all-inherit).

## Navigation

- Parent: `registering-custom-properties` — Registering Custom Properties in JS
- Next: `the-propertydefinition-dictionary` — The PropertyDefinition Dictionary
- Children: 3
  - `dom-css-registerproperty` — registerProperty(PropertyDefinition definition)
  - `register-a-custom-property` — register a custom property
  - `computationally-independent` — computationally independent

## Outgoing refs (14)

`webspec-index refs CSS-PROPERTIES-VALUES-API-1#the-registerproperty-function -d outgoing -l 14`

## Incoming refs (1)

- CSS-PROPERTIES-VALUES-API-1#contents

### Possible effects

CSS-PROPERTIES-VALUES-API-1#the-registerproperty-function

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-PROPERTIES-VALUES-API-1#the-registerproperty-function" --format markdown`
