# Installed-browser relative atan2 observation

The root agent executed the exact sealed probe from `css-atan2-relative-zero-probe-v1/probe.js`, wrapped in `executed.js`, in an owned data-URL tab using the Firefox DevTools MCP. The tool reported System Firefox 158.0. The owned tab and server-started browser session were closed after the observation.

All four relative-unit expressions were already serialized as constant angles. At font size 10px, all eight initial/recovery snapshots matched the literal and resolved-pixel controls. At font size 0px, all four relative expressions disagreed with those controls. All twelve resolved-pixel controls matched the literals. The positive-positive case retained 45deg instead of the zero-degree result of atan2(0px, 0px).

RAW-MCP.json preserves the returned text, OBSERVATIONS.json its parsed data, and FIREFOX-INFO.json the reported configuration. The MCP serialization represents negative zero as a string in the returned expectedDegrees field; the probe records signed coordinate strings explicitly. Rotation matrices cannot distinguish positive from negative 180deg.

This is browser evidence for a source/spec lead, not a fixed or accepted bug. No local native candidate was installed for this run. Binary BuildID, SourceStamp and the full profile preference set were not independently attested, so this is not a claim about a pristine release profile or a controlled before/after comparison.
