# CSS-PROPERTIES-VALUES-API-1#parsing-custom-properties

**Parse-Time Behavior** (heading)

**SHA**: hash:959d45c42d151096bbc21a074aff849f48c64f3f393dfc285c437eb326f066c7

## Content

[Registered custom properties](https://www.w3.org/TR/css-properties-values-api-1#registered-custom-property) parse exactly like unregistered [custom properties](https://www.w3.org/TR/css-variables-1/#custom-property); almost anything is allowed. The registered syntax of the property is *not* checked at parse time.

> **Note:** Note: However, the syntax is checked at computed-value time, before substitution via [var()](https://www.w3.org/TR/css-variables-1/#funcdef-var). See [§ 2.4 Computed Value-Time Behavior](https://www.w3.org/TR/css-properties-values-api-1#calculation-of-computed-values).

Why aren’t custom properties syntax-checked?

When parsing a page’s CSS, UAs commonly make a number of optimizations to help with both speed and memory.

One of those optimizations is that they only store the properties that will actually have an effect; they throw away invalid properties, and if you write the same property multiple times in a single declaration block, all but the last valid one will be thrown away. (This is an important part of CSS’s error-recovery and forward-compatibility behavior.)

This works fine if the syntax of a property never changes over the lifetime of a page. If a custom property is registered, however, it can change its syntax, so that a property that was previously invalid suddenly becomes valid.

The only ways to handle this are to either store every declaration, even those that were initially invalid (increasing the memory cost of pages), or to re-parse the entire page’s CSS with the new syntax rules (increasing the processing cost of registering a custom property). Neither of these are very desirable.

Further, UA-defined properties have their syntax determined by the version of the UA the user is viewing the page with; this is out of the page author’s control, which is the entire reason for CSS’s error-recovery behavior and the practice of writing multiple declarations for varying levels of support. A custom property, on the other hand, has its syntax controlled by the page author, according to whatever stylesheet or script they’ve included in the page; there’s no unpredictability to be managed. Throwing away syntax-violating custom properties would thus only be, at best, a convenience for the page author, not a necessity like for UA-defined properties.

## Navigation

- Parent: `behavior-of-custom-properties` — Registered Custom Properties
- Prev: `determining-registration` — Determining the Registration
- Next: `specified-value` — Specified Value-Time Behavior

## Outgoing refs (4)

- CSS-PROPERTIES-VALUES-API-1#registered-custom-property
- CSS-VARIABLES-1#custom-property
- CSS-VARIABLES-1#funcdef-var
- CSS-PROPERTIES-VALUES-API-1#calculation-of-computed-values

## Incoming refs (2)

- CSS-PROPERTIES-VALUES-API-1#conditional-rules
- CSS-PROPERTIES-VALUES-API-1#contents
