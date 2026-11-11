# WEB-ANIMATIONS-1#animation-property-name-to-idl-attribute-name

**animation property name to IDL attribute name** (algorithm)

**SHA**: hash:cd72b5821823c7cfde12f892b8f0725078b841004b5824f4701afffaafdf5649

## Content

The **animation property name to IDL attribute name** algorithm for *property* is as follows:

1. If *property* follows the [\<custom-property-name>](CSS-VARIABLES-2#typedef-custom-property-name) production, return *property*.
2. If *property* refers to the CSS [float](CSS2#propdef-float) property, return the string "cssFloat".
3. If *property* refers to the CSS [offset](MOTION-1#propdef-offset) property, return the string "cssOffset".
4. Otherwise, return the result of applying the [CSS property to IDL attribute](CSSOM#css-property-to-idl-attribute) algorithm \[CSSOM\] to *property*.

## Navigation

- Parent: `property-name-conversion` — Property names and IDL names
- Next: `idl-attribute-name-to-animation-property-name` — IDL attribute name to animation property name

## Outgoing refs (4)

- CSS-VARIABLES-2#typedef-custom-property-name
- CSS2#propdef-float
- MOTION-1#propdef-offset
- CSSOM#css-property-to-idl-attribute

## Incoming refs (3)

- WEB-ANIMATIONS-1#index-defined-here
- WEB-ANIMATIONS-1#process-a-keyframe-like-object
- WEB-ANIMATIONS-1#the-keyframeeffect-interface

### Possible effects

WEB-ANIMATIONS-1#animation-property-name-to-idl-attribute-name

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "WEB-ANIMATIONS-1#animation-property-name-to-idl-attribute-name" --format markdown`
