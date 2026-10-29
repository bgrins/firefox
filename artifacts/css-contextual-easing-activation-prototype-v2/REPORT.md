# Body-availability fixture correction

The actual original-app 293-case run reported all sixteen new tests failing because document.body was null: promise_test callbacks began while the pages were still parsing their head. Those sixteen results are fixture failures, not native contextual-easing failures. Root raw inspection e1d153 identified the error; the original sealed activation-v1 and its raw runtime remain unchanged.

This successor adds an explicit <body> immediately before the inline test script in both pages. All test callbacks, sixteen names, numeric oracles, control setup, cleanup and native eight-source bodies are byte-identical. The complete native patch and source-role map are unchanged. The one easing candidate stored in activation-v1 is now an external authenticated reference, like the other seven candidates.

The earlier inert registration and lint checks did not execute callbacks and therefore did not detect this DOM readiness error. Fresh original execution is required before interpreting the sixteen new outcomes. The root separately reports three upstream contextual targets genuinely FAIL and controls259PASS/15FAIL; those are not replaced by expectations for these fixtures.

All activation-v1 source and semantic boundaries remain: experimental CSS parser activation, fallible context-free API, unsupported variable-bearing keyframe path, unresolved animation-only/feedback/Servo obligations, and no complete acceptance claim. This is only a fixture correction; no native source or browser action occurs here.
