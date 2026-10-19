# Repeated NaN CSSOM assignment: normative trace

Read current primary drafts on 2026-10-19 through the web tool. These notes are a selected trace, not a complete downloaded specification.

1. [CSS Values 4 math constants](https://drafts.csswg.org/css-values-4/#calc-keywords) permits NaN as a number inside calculations. Multiplying by a unit supplies the required dimensional type. Top-level resolution censors NaN to zero; that does not establish how a specified calculation must be represented internally.
2. [CSSOM setProperty](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty) parses the property value, sets the declaration, and updates the style attribute when the returned flag is true.
3. [Set a CSS declaration](https://drafts.csswg.org/cssom/#set-a-css-declaration) constrains target uniqueness/value/importance, unrelated declarations and logical ordering. A changed serialization requires true; an unchanged serialization permits false without requiring it. Its suggested equality-based algorithm is one permitted implementation.
4. [Update style attribute](https://drafts.csswg.org/cssom/#update-style-attribute-for) sets the owner's style attribute when an owner exists.
5. [DOM change an attribute](https://dom.spec.whatwg.org/#concept-element-attributes-change) handles attribute changes without a same-string early return. Handling queues the mutation record and, where applicable, a custom-element callback.

Verdict: NOT REACHED for the claim that an unchanged repeated assignment MUST suppress mutation records. A conservative native comparator returning false for NaN can cause a permitted publication. This conclusion does not equate identical serialization with semantic value equality.
