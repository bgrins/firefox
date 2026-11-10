# CSSOM#dom-window-getcomputedstyle

**getComputedStyle(elt, pseudoElt)** (algorithm)

**SHA**: hash:445e6715c91451921e7041747a7f3ef728eeef16009e573c35181854d46f6304

## Content

The **`getComputedStyle(*elt*, *pseudoElt*)`** method must run these steps:

1. Let *doc* be *elt*’s [node document](https://dom.spec.whatwg.org/#concept-node-document).
2. Let *obj* be *elt*.
3. If *pseudoElt* is provided, is not the empty string, and starts with a colon, then:

    1. [Parse](https://drafts.csswg.org/css-syntax-3/#css-parse-something-according-to-a-css-grammar) *pseudoElt* as a [\<pseudo-element-selector>](https://drafts.csswg.org/selectors-4/#typedef-pseudo-element-selector), and let *type* be the result.
    2. If *type* is failure, or is a [::slotted()](https://drafts.csswg.org/css-shadow-1/#selectordef-slotted) or [::part()](https://drafts.csswg.org/css-shadow-1/#selectordef-part) pseudo-element, let *obj* be null.
    3. Otherwise let *obj* be the given pseudo-element of *elt*.


    > **Note:** Note: CSS2 pseudo-elements should match both the double and single-colon versions. That is, both `:before` and `::before` should match above.
4. Let *decls* be an empty list of [CSS declarations](https://drafts.csswg.org/cssom#css-declaration).
5. If *obj* is not null, and *elt* is [connected](https://dom.spec.whatwg.org/#connected), part of the [flat tree](https://drafts.csswg.org/css-shadow-1/#flat-tree), and its [shadow-including root](https://dom.spec.whatwg.org/#concept-shadow-including-root) has a [browsing context](https://html.spec.whatwg.org/multipage/browsers.html#browsing-context) which either doesn’t have a browsing context container, or whose browsing context container is [being rendered](https://html.spec.whatwg.org/multipage/rendering.html#being-rendered), set *decls* to a list of all longhand properties that are [supported CSS properties](https://drafts.csswg.org/cssom#supported-css-property), in lexicographical order, with the value being the [resolved value](https://drafts.csswg.org/cssom#resolved-value) computed for *obj* using the style rules associated with *doc*. Additionally, append to *decls* all the [custom properties](https://drafts.csswg.org/css-variables-1/#custom-property) whose [computed value](https://drafts.csswg.org/css-cascade-5/#computed-value) for *obj* is not the [guaranteed-invalid value](https://drafts.csswg.org/css-variables-2/#guaranteed-invalid-value).

    > **Issue:** There are UAs that handle shorthands, and all UAs handle shorthands that used to be longhands like [overflow](https://drafts.csswg.org/css-overflow-3/#propdef-overflow), see [#2529](https://github.com/w3c/csswg-drafts/issues/2529).

    > **Issue:** Order of custom properties is currently undefined, see [#4947](https://github.com/w3c/csswg-drafts/issues/4947).
6. Return a live [`CSSStyleProperties`](https://drafts.csswg.org/cssom#cssstyleproperties) object with the following properties:

    [computed flag](https://drafts.csswg.org/cssom#cssstyledeclaration-computed-flag) 

    Set.

    [readonly flag](https://drafts.csswg.org/cssom#cssstyledeclaration-readonly-flag) 

    Set.

    [declarations](https://drafts.csswg.org/cssom#cssstyledeclaration-declarations) 

    *decls*.

    [parent CSS rule](https://drafts.csswg.org/cssom#cssstyledeclaration-parent-css-rule) 

    Null.

    [owner node](https://drafts.csswg.org/cssom#cssstyledeclaration-owner-node) 

    *obj*.

## Navigation

- Parent: `extensions-to-the-window-interface` — Extensions to the Window Interface

## Outgoing refs (23)

`webspec-index refs CSSOM#dom-window-getcomputedstyle -d outgoing -l 23`

## Incoming refs (4)

- CSSOM#extensions-to-the-window-interface
- CSSOM#idl-index
- CSSOM#index-defined-here
- CSSOM#resolved-values

### Possible effects

CSSOM#dom-window-getcomputedstyle

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSSOM#dom-window-getcomputedstyle" --format markdown`

Makes 1 call: `webspec-index state CSSOM#dom-window-getcomputedstyle --calls`
