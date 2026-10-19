# Namespaced typed attr collision probe

Status: unexecuted browser/WPT candidate. No production changes.

Serve this directory and open `probe.html`; after load, read `window.__attrNamespaceProbe`. It contains eight rows: two predicted discrepancies and six controls. CSSOM/DOM/support/calibration evidence is separate from expected and source-predicted values. `wpt-candidate.html` uses the same probe.css/probe.js and requires the WPT `/resources/` harness; it declares nine tests (one calibration, eight rows). Copy all three files together when installing the candidate.

The browser page is standalone apart from its two sibling resources. `node --check probe.js` passed; no browser, build, Mach or WPT command was run by this agent.

SPEC-TRACE.md gives the independent primary-spec expectation. SOURCE-TRACE.md documents the exact native path and prior-art limitation. INPUTS.json pins all files except itself; root owns browser execution and acceptance. Please retain this frozen package before executing any adapted WPT.
