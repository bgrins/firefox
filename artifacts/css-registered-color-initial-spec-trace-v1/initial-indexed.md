# CSS-PROPERTIES-VALUES-API-1#initial-value-descriptor

**The initial-value Descriptor** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

| Name:                                                                                                                                  |
| -------------------------------------------------------------------------------------------------------------------------------------- |
| [@property](CSS-PROPERTIES-VALUES-API-1#at-ruledef-property)                                                     |
| [\<declaration-value>](CSS-SYNTAX-3#typedef-declaration-value)[?](CSS-VALUES-4#mult-opt) |
| the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value) (but see prose)                        |

Specifies the initial value of the [custom property registration](CSS-PROPERTIES-VALUES-API-1#custom-property-registration) represented by the [@property](CSS-PROPERTIES-VALUES-API-1#at-ruledef-property) rule, controlling the property’s [initial value](CSS-CASCADE-5#initial-value).

If the value of the [syntax](CSS-PROPERTIES-VALUES-API-1#descdef-property-syntax) descriptor is the [universal syntax definition](CSS-PROPERTIES-VALUES-API-1#universal-syntax-definition), then the [initial-value](CSS-PROPERTIES-VALUES-API-1#descdef-property-initial-value) descriptor is optional. If omitted, the [initial value](CSS-CASCADE-5#initial-value) of the property is the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value).

Otherwise, if the value of the [syntax](CSS-PROPERTIES-VALUES-API-1#descdef-property-syntax) descriptor is not the [universal syntax definition](CSS-PROPERTIES-VALUES-API-1#universal-syntax-definition), the following conditions must be met for the [@property](CSS-PROPERTIES-VALUES-API-1#at-ruledef-property) rule to be valid:

*   The [initial-value](CSS-PROPERTIES-VALUES-API-1#descdef-property-initial-value) descriptor must be present.

*   The [initial-value](CSS-PROPERTIES-VALUES-API-1#descdef-property-initial-value) descriptor’s value must [parse successfully](CSS-PROPERTIES-VALUES-API-1#consume-a-syntax-definition) according to the grammar specified by the [syntax definition](CSS-PROPERTIES-VALUES-API-1#syntax-definition).

*   The [initial-value](CSS-PROPERTIES-VALUES-API-1#descdef-property-initial-value) must be [computationally independent](CSS-PROPERTIES-VALUES-API-1#computationally-independent).

If the above conditions are not met, the [@property](CSS-PROPERTIES-VALUES-API-1#at-ruledef-property) rule is invalid.

## Navigation

- Parent: `at-property-rule` — The @property Rule
- Prev: `inherits-descriptor` — The inherits Descriptor
- Children: 1
  - `descdef-property-initial-value` — initial-value

## Outgoing refs (12)

`webspec-index refs CSS-PROPERTIES-VALUES-API-1#initial-value-descriptor -d outgoing -l 12`

## Incoming refs (1)

- CSS-PROPERTIES-VALUES-API-1#contents

### Possible effects

CSS-PROPERTIES-VALUES-API-1#initial-value-descriptor

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-PROPERTIES-VALUES-API-1#initial-value-descriptor" --format markdown`
