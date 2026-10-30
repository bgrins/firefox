# CSS-CASCADE-5#cascade-sort

**Cascade Sorting Order** (heading)

**SHA**: hash:2c51fc71d5bfec21aee9acf5004344fc0b5197db31fc48a1ae5373f3fbc4670f

## Content

The cascade sorts [declarations](https://drafts.csswg.org/cssom-1/#cssstyledeclaration-declarations) according to the following criteria, in descending order of precedence:

Origin and Importance 

The [origin](https://drafts.csswg.org/css-cascade-5#origin) of a [declaration](https://drafts.csswg.org/css-syntax-3/#declaration) is based on where it comes from and its [importance](https://drafts.csswg.org/css-cascade-5#important) is whether or not it is declared with !important (see [below](https://drafts.csswg.org/css-cascade-5#importance)). The precedence of the various origins is, in descending order:

1.  Transition declarations \[css-transitions-1\]
2.  [Important](https://drafts.csswg.org/css-cascade-5#important) [user agent](https://drafts.csswg.org/css-cascade-5#cascade-origin-ua) declarations
3.  [Important](https://drafts.csswg.org/css-cascade-5#important) [user](https://drafts.csswg.org/css-cascade-5#cascade-origin-user) declarations
4.  [Important](https://drafts.csswg.org/css-cascade-5#important) [author](https://drafts.csswg.org/css-cascade-5#cascade-origin-author) declarations
5.  Animation declarations \[css-animations-1\]
6.  [Normal](https://drafts.csswg.org/css-cascade-5#normal) [author](https://drafts.csswg.org/css-cascade-5#cascade-origin-author) declarations
7.  [Normal](https://drafts.csswg.org/css-cascade-5#normal) [user](https://drafts.csswg.org/css-cascade-5#cascade-origin-user) declarations
8.  [Normal](https://drafts.csswg.org/css-cascade-5#normal) [user agent](https://drafts.csswg.org/css-cascade-5#cascade-origin-ua) declarations

Declarations from [origins](https://drafts.csswg.org/css-cascade-5#origin) earlier in this list win over declarations from later origins.

Context 

A document language can provide for blending [declarations](https://drafts.csswg.org/cssom-1/#cssstyledeclaration-declarations) sourced from different **encapsulation contexts**, such as the nested [tree contexts](https://drafts.csswg.org/css-shadow-1/#tree-context) of [shadow trees](https://dom.spec.whatwg.org/#concept-shadow-tree) in the \[DOM\].When comparing two declarations that are sourced from different [encapsulation contexts](https://drafts.csswg.org/css-cascade-5#encapsulation-contexts), then for [normal](https://drafts.csswg.org/css-cascade-5#normal) rules the declaration from the outer context wins, and for [important](https://drafts.csswg.org/css-cascade-5#important) rules the declaration from the inner context wins. For this purpose, \[DOM\] [tree contexts](https://drafts.csswg.org/css-shadow-1/#tree-context) are considered to be nested in [shadow-including tree order](https://dom.spec.whatwg.org/#concept-shadow-including-tree-order).

> **Note:** Note: This effectively means that [normal](https://drafts.csswg.org/css-cascade-5#normal) declarations belonging to an [encapsulation context](https://drafts.csswg.org/css-cascade-5#encapsulation-contexts) can set defaults that are easily overridden by the outer context, while [important](https://drafts.csswg.org/css-cascade-5#important) declarations belonging to an encapsulation context can enforce requirements that cannot be overridden by the outer context.

Element-Attached Styles 

Separately for [normal](https://drafts.csswg.org/css-cascade-5#normal) and [important](https://drafts.csswg.org/css-cascade-5#important) [declarations](https://drafts.csswg.org/cssom-1/#cssstyledeclaration-declarations), declarations that are attached directly to an element (such as the [contents of a style attribute](https://www.w3.org/TR/css-style-attr/#interpret)) rather than indirectly mapped by means of a style rule selector take precedence over declarations the same importance that are mapped via style rule.See \[CSSSTYLEATTR\].

> **Note:** Note: Non-CSS presentational hints (such as presentational markup) are handled separately, see [§ 6.5 Precedence of Non-CSS Presentational Hints](https://drafts.csswg.org/css-cascade-5#preshint).

Layers 

[Declarations](https://drafts.csswg.org/cssom-1/#cssstyledeclaration-declarations) within each [origin](https://drafts.csswg.org/css-cascade-5#origin) and [context](https://drafts.csswg.org/css-cascade-5#encapsulation-contexts) can be explicitly assigned to a [cascade layer](https://drafts.csswg.org/css-cascade-5#cascade-layers). For the purpose of this step, any declaration not assigned to an explicit layer is added to an implicit final layer.Cascade layers (like declarations) are sorted by order of appearance, see [§ 6.4.3 Layer Ordering](https://drafts.csswg.org/css-cascade-5#layer-ordering). When comparing declarations that belong to different layers, then for [normal](https://drafts.csswg.org/css-cascade-5#normal) rules the declaration whose [cascade layer](https://drafts.csswg.org/css-cascade-5#cascade-layers) is latest in the layer order wins, and for [important](https://drafts.csswg.org/css-cascade-5#important) rules the declaration whose cascade layer is earliest wins.

> **Note:** Note: This follows the same logic used for precedence of [normal](https://drafts.csswg.org/css-cascade-5#normal) and [important](https://drafts.csswg.org/css-cascade-5#important) [origins](https://drafts.csswg.org/css-cascade-5#origin), thus the !important flag maintains the same “override” purpose in both settings.

Specificity 

The [Selectors module](https://www.w3.org/TR/selectors/#specificity) \[SELECT\] describes how to compute the specificity of a selector. Each [declaration](https://drafts.csswg.org/css-syntax-3/#declaration) has the same specificity as the style rule it appears in. The declaration with the highest specificity wins.

Order of Appearance 

The last [declaration](https://drafts.csswg.org/css-syntax-3/#declaration) in document order wins. For this purpose:

*   Style sheets are ordered in [final CSS style sheets](https://drafts.csswg.org/cssom-1/#documentorshadowroot-final-css-style-sheets) order.
*   Declarations from [imported style sheets](https://drafts.csswg.org/css-cascade-5#at-ruledef-import) are ordered as if their style sheets were substituted in place of the @import rule.
*   Declarations from style sheets independently linked by the originating document are treated as if they were concatenated in linking order, as determined by the host document language.
*   Declarations from style attributes are ordered according to the document order of the element the style attribute appears on, and are all placed after any style sheets. \[CSSSTYLEATTR\]

The **output of the cascade** is a (potentially empty) sorted list of [declared values](https://drafts.csswg.org/css-cascade-5#declared-value) for each property on each element.

## Navigation

- Parent: `cascading` — Cascading
- Next: `cascading-origins` — Cascading Origins
- Children: 8
  - `cascade-origin` — Origin and Importance
  - `cascade-context` — Context
  - `encapsulation-contexts` — encapsulation contexts
  - `style-attr` — Element-Attached Styles
  - `cascade-layering` — Layers
  - `cascade-specificity` — Specificity
  - `cascade-order` — Order of Appearance
  - `output-of-the-cascade` — output of the cascade

## Outgoing refs (21)

`webspec-index refs CSS-CASCADE-5#cascade-sort -d outgoing -l 21`

## Incoming refs (1)

- CSS-CASCADE-5#contents
