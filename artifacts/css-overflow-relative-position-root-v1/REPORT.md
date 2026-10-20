# Root acceptance: relative positioning of overflow continuations

Accepted within the scope in ACCEPTANCE.json. Both changes are necessary: read
predecessor normal inline position, then enable relative positioning for the
current relative continuation when finishing reflow. This avoids inherited inline
double-counting, restores block translation, and initializes the current normal
property for later updates. Sticky and nonrelative branches remain unchanged.

Root inspected the exact native delta, independent source/caller/lifecycle
review, standalone WPT and the source-bound model. Finish installs the actual
returned size before conversion, and the predecessor normal getter uses the
predecessor size. Current offsets are supplied by the current ReflowInput.
Actual Default caller flags and frame-aware relative applicability are preserved.

The original140-case pair fixes30 failures; the supplementary280-case RTL pair
fixes60, with all prior passes retained. Existing35/61 file outcomes are unchanged,
including expected failures. Candidate/restoration builds pass. WPT lint is clean.
Actual-path formatting only changes one argument-list line break; the exact
single replacement is authenticated in FORMAT-BRIDGE.json. Root applied and
reversed that final two-file patch without fuzz and recovered exact source/test.

Root authenticated and freshly replayed the86-payload formal capsule from a
manifest-only relocation:33kernel audits,4falseclaims,2axiom guards, genuine
before/candidate216case runs atO0/O2,8compiled mutant detections and raw runtime
recounts pass. Four intentionally failing before/candidate UBSan boundary cases
remain explicit: a final coordinate that fits does not imply safe rect-end
addition. Source generation and patch recovery pass. Fresh integrity controls
reject unexpected files, caches, modified proof and source-role substitution.
The independent native review checker also passed under root execution.

Full lifecycle scope remains HOLD. Predecessor property correctness, callback
and offset-provider truth, all-coordinate bounds, skipped/reparented frames,
continuation graph/status/overflow observers remain admissions or open work.
The proof establishes the stated source-coordinate relation, not full CSS or
native memory safety. Runtime uses the shared combined project tree. Compiler
products were temporary and removed by replay. No signed commit or push has
occurred; the native patch has separate evidence/formal companions.
