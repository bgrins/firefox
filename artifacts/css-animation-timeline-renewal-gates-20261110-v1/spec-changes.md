# CSS-VARIABLES-1#changes

**Changes** (heading)

**SHA**: hash:72c4b00afaa33f30ded58f4b1e4595c7155bb410d01e0d24b8157cdbdf101e40

## Content

### Changes Since the 16 June 2022 CR Snapshot

*   Clarified that the comment-insertion can happen with 0+ comments between the original tokens, not just exactly 1.

*   Clarified the transition behavior of custom properties, in a note

*   Made [var()](CSS-VARIABLES-1#funcdef-var) short-circuiting. ([Issue 11500](https://github.com/w3c/csswg-drafts/issues/11500))

### Changes Since the 11 November 2021 CR Draft

*   Clarified that custom properties apply all pseudo-elements (including those with restricted property lists)

*   Added example to illustrate issues with combining characters, ligatures, etc

*   Strengthened wording around similar-appearing variable names that use distinct codepoint sequences

*   Clarified an example by using more visually distinct languages as examples (English and Greek)

*   Split Security and Privacy into separate sections

### Changes Since the 03 December 2015 CR

*   Now that \[css-syntax-3\] auto-trims whitespace from declaration values, made [\<declaration-value>](CSS-SYNTAX-3#typedef-declaration-value) optional in the custom property grammar, so that empty variables are still allowed. ([Issue 774](https://github.com/w3c/csswg-drafts/issues/774#issuecomment-434571254))

*   Similarly, made empty fallbacks valid in [var()](CSS-VARIABLES-1#funcdef-var).

*   The -- property is reserved for future use by CSS.

*   Added concept of "animation-tainted", to prevent non-animatable properties from using a variable to smuggle in some animatability.

*   Defined the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value) to make the initial value of custom properties and the result of cycles or substitution failure more straightforward, and allow failure to propagate thru substitutions until finally intercepted by a fallback.

*   Defined that cycles trigger [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time) behavior.

*   Allowed variables to resolve to a CSS-wide keyword (only possible by providing it as a fallback).

*   Clarified that [registered custom properties](https://drafts.css-houdini.org/css-properties-values-api-1/#registered-custom-property) act like non-custom properties when they’re [invalid at computed-value time](CSS-VALUES-5#invalid-at-computed-value-time).

*   Made longhands with [var()](CSS-VARIABLES-1#funcdef-var)s also trigger their shorthands to be unserializable, like longhands with pending-substitution values already did.

*   Required UAs to defend against exponential substitution attacks.

*   Defined how to serialize the *values* of custom properties (previously, only the property name’s serialization was specified).

### Changes since the May 6 2014 Last Call Working Draft

*   Serialization of longhands when shorthand uses a variable was defined.

*   Link to DOM’s definition of "case-sensitive".

*   Added example of using variables with [:lang()](SELECTORS-4#lang-pseudo) to do simple i18n.

*   Clarified that usage of [var()](CSS-VARIABLES-1#funcdef-var) in a custom property must be valid per the var() grammar.

## Navigation

- Prev: `apis` — APIs
- Next: `acks` — Acknowledgments
- Children: 4
  - `changes-20220616` — Changes Since the 16 June 2022 CR Snapshot
  - `changes-20211111` — Changes Since the 11 November 2021 CR Draft
  - `changes-20151203` — Changes Since the 03 December 2015 CR
  - `changes-20140506` — Changes since the May 6 2014 Last Call Working Draft

## Incoming refs (1)

- CSS-VARIABLES-1#contents

### Possible effects

CSS-VARIABLES-1#changes

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VARIABLES-1#changes" --format markdown`
