# Loaded FontFace descriptor reproduction

`ROOT-BASELINE-v2.json` records the valid local browser baseline: four fresh-face
controls pass and eight loaded `sizeAdjust` mutations fail for URL and buffer
sources. At 20px, four Ahem glyphs remain 80px wide after changing 100% to 50%,
instead of becoming 40px. Mutating before first addition also fails.

The WPT source and all pinned nonbinary inputs are in `baseline-v2-sources/`.
The live WPT is reserved for the eventual standalone native-fix commit.
`baseline-v2-receipt.json`, its raw JSONL and log retain the full run, including
two existing expected failures. The first run's cleanup callback returned a
boolean and caused a harness error; `baseline-v1` is invalidated evidence.

The standalone probe lives in the separate frozen
`../css-fontface-provider-update-scout-v1/probes/` directory. The MCP system
Firefox reported version 158.0 and reproduced five failures with four passes;
that executable was not bound to the checkout build. See `system-browser.json`.

This was a static-code finding followed by browser confirmation, within the
known bug 1072149 descriptor-update family. It was not discovered by a Lean
proof. The conceptual design in `../css-fontface-provider-proof-v1/REPORT.md`
has 13 small identity/publication theorems; root's fresh relocated replay passes.
They do not establish native implementation correctness or a completed repair.

The repair must preserve independent FontFace objects even when they share a
wrapper or platform entry, retain consumed buffer resources and loaded promises,
and update every document/worker membership. Resource-preserving local-font
handling, worker publication, and failure rollback are still under design.
