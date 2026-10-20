# Overflow child branch trace

The temporary instrumented candidate built and ran the four-stage minimal vertical-rl diagnostic, then restored both original source files and the browser build. All commands exited0; HEAD and staged binary diff remained unchanged. The source and instrumented complete files are retained.

Twelve eligible helper visits all took reflow: parent DIRTY, child subtree dirty, and ShouldReflowAllKids were true on every visit. None executed skip. Old/final parent widths include4800→4860→4800appunits, but those visits reflowed the child. All four DOM stages produced the expected descendant coordinates. This is evidence for exercised paths only and does not establish the hypothetical skipped-child width invariant.

Instrumentation logs actual guard values and frame positions before/after helper processing. The overflow-exceeds predicate is evaluated for the log only when the original short-circuit would reach it; no such extra evaluation happened in this run. Instrumentation is still a changed binary and is not a proof of equivalence to the production helper. The previous-in-flow-parent early-continue is outside these trace records.

Source review identified a concrete propagation route from a previous column's NextInFlowNeedsReflow through nsColumnSetFrame::ReflowColumns calling MarkSubtreeDirty on the next column. This trace does not identify which dirtying route actually ran. Exact skip reachability, continuation-list lifecycle, and broad regression review remain open. No repair acceptance follows from this trace.
