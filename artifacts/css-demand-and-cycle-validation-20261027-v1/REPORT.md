# Demand validation and cycle investigation checkpoint

The typed-demand prototype now passes its full native build and all 20 selected GTests across four suites, including the new test’s 22 real resolver calls. Only the two GTest XUL files changed in that host-test phase; normal Firefox/XUL stayed pinned. The prepared four ordinary substitution WPTs produced 253 PASS and three existing expected FAIL subtests, four OK harness endings, and no unexpected results. Their exact source bodies, inherited metadata, resources, isolated runner inputs, source/binary hashes and root/nested preservation checks passed.

These results validate the callable resolver prototype and this ordinary regression set. They do not enable or verify the unfinished production pending-provider collector/scheduler. The attr-cycle test’s existing raw-string oracle is retained as a regression condition, not proof against the newer spec trace.

Both attribute-cycle leads reproduce on local Nightly 160 with every row identical to release Firefox 158: raw nested reads show five disagreements/eight passing controls; used bare/unit fallbacks show seven disagreements/six passing controls. The root independently checked the current Values 5 raw-return and used-fallback guarded-cycle paths. These are now repair targets, not accepted fixes.

A focused registered-number probe reproduces seven release disagreements and identifies one additional local control failure. The existing unfinished numeric dependency widening is a plausible cause of that extra path; a controlled comparison is still needed. Preserve arithmetic support and distinguish reached operands from unused/invalid token branches. The older length-syntax graph rule remains a separate spec ambiguity.

All 135 accepted fixes remain separate signed native/WPT commits. This batch adds validation and investigative evidence only. No push, Try or Phabricator action.
