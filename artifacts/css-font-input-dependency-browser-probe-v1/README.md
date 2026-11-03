# Font input dependency preservation controls

System Firefox 158 produced 48 matching first-read observations: six consuming
properties, four font-size forms, and sizes changing from 20px to 30px. Each
registered `--unit: 1em` value matched both the corresponding reference and the
literal expected size. All tested declaration forms passed CSS.supports.

The consuming properties are appearance, direction, text-orientation,
writing-mode, font-family and font-weight. Font sizes are absolute, variable,
percentage and inherited. The target's attribute contains `var(--unit)` and its
typed length is used in a declaration whose property expects another type.
The first observation reads the registered custom property before the other
computed-style getters. The document was in standards mode.

These are preservation controls, not newly discovered failures. The browser was
the connector's System Firefox, not a source-bound original/candidate build.
No local-branch or experimental implementation pass follows from this result.
Replacing the stylesheet between observations also does not isolate attribute
mutation invalidation. The observation checks the registered length; it does
not assert that every consuming property's value equals its fallback keyword.

`probe.js` is the evaluated function; `browser-result.json` retains the original
tool response and `observations.json` its extracted observations. The iframe is
removed in a finally block. Root closed the probe tab and the server-owned
browser session after extraction (terminal 79d849).
