# Repeated attribute invalidation/reload probe

Status: unexecuted. Serve probe.html with probe.css/probe.js beside it, then read window.__attributeReloadProbe. There are ten rows, four predicted discrepancies and six expected controls. The WPT candidate uses those same two sibling resources and declares eleven tests including calibration.

The result includes raw computed `--out` text, second-property text for the independent-declaration control, margins, specified CSSOM, DOM attributes, missing-custom-property readback and width/containing-block calibration. Node syntax validation passed; no browser/WPT/build command was run by this agent.

SPEC-TRACE.md supplies the independent current-spec expectation. SOURCE-TRACE.md gives the exact repeated-visit transition sequence. INPUTS.json freezes the package; root owns browser execution and adjudication. Keep this separate from fallback preload/type-fallback scouts.
