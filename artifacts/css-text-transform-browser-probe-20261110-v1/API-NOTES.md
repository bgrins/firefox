# Browser API observation boundary

Preparation consulted the current [CSSOM setProperty algorithm](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty), Editor's Draft dated 13 October 2026, and [CSS Conditional 3 supports API](https://drafts.csswg.org/css-conditional-3/#dom-css-supports), dated 8 October 2026, on 2026-11-11 UTC. These are protocol guidance, not additional mechanically proved or archived spec modules.

Empty setProperty values take the property-removal path. Accordingly the empty corpus row expects no grammar acceptance, records a fresh declaration without that property, and separately seeds uppercase then observes removal. A setter that returns normally has not thereby accepted a value: for nonempty values, the probe checks the resulting declaration name list and nonempty property value. CSS.supports uses its two-argument form.

Serialized text and declaration cssText are recorded. No assertion compares token ordering, canonical spelling or cssText formatting to the input. The analyzer only requires consistency between property presence, the declaration list and whether a value exists. No computed style or rendering is queried.
