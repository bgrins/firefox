# Expected metric behavior

Registered `<length>` literals compute in their canonical unit. Here registration is non-inheriting with valid independent initial 0px, and the specified values are direct 1em/1ch literals with no custom-property cycle. The custom value should therefore agree with a literal width using the same unit and font style. [Properties and Values §2.4](https://drafts.css-houdini.org/css-properties-values-api-1/#computed-value-time).

`em` uses the element’s font size; `ch` uses the advance of its selected zero glyph in the inline direction. The fixture fixes horizontal writing mode and ordinary text orientation, font style/stretch and size adjustment. It compares against measured same-style references, not hardcoded operating-system metrics. Changing family or selecting another weight face must affect 1ch when the independently measured controls differ, while 1em retains 20px/30px. [CSS Values §6.1.1](https://www.w3.org/TR/css-values-4/#font-relative-lengths).

Font-face descriptors provide matching family/weight properties for downloadable faces. The weight callback maps Ahem to 400 and Noto to 700 under one artificial family, deliberately giving two distinguishable selected faces. This is a font selection control, not a claim that real-world bold fonts necessarily have different character widths. [CSS Fonts font-face descriptors](https://www.w3.org/TR/css-fonts-4/#font-prop-desc).

The fixture explicitly loads the matching face for each family/weight using the zero character, checks the returned face is loaded, then awaits document.fonts.ready before creating metric targets. This avoids treating a pending font download as a scheduling failure. [CSS Font Loading load](https://drafts.csswg.org/css-font-loading/#font-face-set-load), [ready](https://drafts.csswg.org/css-font-loading/#font-face-set-ready).

Primary pages were read through the web tool during preparation. The css-values editor-draft fetch failed, so the published CSS Values4 text was used. This basis defines expected observable values; it does not prove an internal graph edge, native execution order or a current Firefox defect.

Root additionally checked the CSS Values4 editor draft dated 24 August 2026 and PVAPI1 draft dated 6 August 2026, confirming the same rules. The registered metric is not consumed by a font-affecting declaration, so the parent-metric exception for font-property values does not apply. Existing font-property-unit-cycles tests corroborate own-element metric resolution but do not cover selected weight changes.
