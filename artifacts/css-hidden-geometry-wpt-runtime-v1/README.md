# Uninstrumented hidden flex WPT experiment

Four variants run against exact committed bytes for all20 currently modified native
files. The only phase-varying file is nsFlexContainerFrame.cpp: committed baseline,
one-line skipped-child dirtying, original four-field measurement key, and original
key plus the same dirtying. This isolates prototypes and both key additions98/101.
It is not a full upstream checkout/runtime: other committed branch fixes remain.

All new fixtures preserve exact geometry and repeated-read controls. Existing
hidden-content and flex cache/continuation tests are retained as regression gates.
Key-dependent tests may fail in original-key phases; compare like-key variants.
Raw WPT status/roster completeness is checked independently of numerical success.
A terminal diagnostic run is not native acceptance. Expanded failures are retained.

The driver pins tests, input source variants, original/head snapshots and runner.
It records all native source pins, HEAD/index before and after, actual binary/test
pins per WPT run, complete raw output and build logs. It restores every original
source and preexisting test byte in finally, removes only its temporary tests and
rebuilds the original sources. It does not change Git history or index. No timing
claims follow from these runs.
