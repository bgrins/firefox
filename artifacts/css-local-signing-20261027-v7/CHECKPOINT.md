# Local signed CSS checkpoint

- animation-completion: `4a676d16c4c2e33f40603a9ca8b9bfd6af786359` (signature verified).
- animation-demand: `b55d38f3d26877a3fcac475208837cc806fcb6a3` (signature verified).
- counter-research: `b70f5b951d84dd9083665f8ca7b61f4a47429db6` (signature verified).
- fallback-version-trace: `2e11730a51ae96154938764c73559de817a7948a` (signature verified).
- typed-attribute-demand: `401c688f4a1cabdfee37899090609718a4372287` (signature verified).
- counter-validation: `7cc4b9b3f524117870d19fff665843fc876d495d` (signature verified).
- counter-fix: `37bc9b06f034c191be50aa4949b072bbf7d5a64e` (signature verified).

Fix 136 repairs contained counter append invalidation. Its standalone commit contains exactly nsCounterManager.cpp, nsCounterManager.h and counter-scoping-append-invalidation.html; the immediate parent contains the evidence. Both original runs reproduce 12 failures and 12 passing controls; both fixed runs pass 24. All 64 quote subtests and 8 existing counter regressions remain passing. Three builds and exact-fixture WPT lint pass. The outer comparison tool handle was lost; archived child exits, successful driver result, independent process/archive review and fresh full live verification provide the completion evidence without inventing an outer exit code.

The five ledgers now list 135 accepted committed fixes, numbered through 136 with held 120 excluded. Lean canonical coverage counts remain unchanged. The new counter model is conditional corroboration after source/browser discovery, not a complete native proof. No clean-upstream build, security or measured performance claim.

The animation scheduler tests pass in isolation; the native scheduler adapter, substitution-demand and typed-attribute/context-demand proposals remain uncompiled and disabled in production. Next: compile the combined demand proposal, execute its 22 proposed resolver calls plus existing tests, then connect actual winning cascade admission and completion. Current-base, cycle-policy, successful-effect publication and memory reporting remain open. The versioned var-fallback trace identifies no new ordinary-cascade bug.

All 131 bodies in the previously committed css-unfinished-work-checkpoint-20261027-v4 recovery snapshot still match. Its 128 unfinished source/fixture/proof bodies remain in the worktree and are not counted as accepted fixes. The newly added counter fix is committed separately. No duplicate source snapshot is needed.

All work remains local. The local refs/codex/css-signing/20261027-v7 recovery ref retains the first five research commits, now ancestors of the branch. Generated staging patches and redundant epoch copies are omitted from this checkpoint. CURRENT-EPOCH.json is the mutable continuation record; signed objects, selected immutable epochs and execution receipts retain provenance.
