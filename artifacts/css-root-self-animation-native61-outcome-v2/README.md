# Native owner-v2 binding preparation

This successor changes only the expected native owner directory from candidate-browser-v1 to candidate-browser-v2. The original prepared audit/comparison body is otherwise byte-identical. Saved checks of raw-stream completeness, baseline normalization and exact signature preservation are reused from the pinned v1 preparation; no repeated execution is claimed.

The future owner/runtime manifest, launch group, actual terminal/result and restoration fields remain pending. Execution is disabled. Root must authenticate the actual owner terminal to RESULT hash before binding and keep independent restoration separate from all-PASS comparison. The runtime remains candidate-browser-runtime-v1, which has not run yet. This preparation does not assert that owner-v2 is sealed, reviewed or executed.
