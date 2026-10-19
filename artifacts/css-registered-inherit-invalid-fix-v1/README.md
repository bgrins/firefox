# Explicit inheritance of invalid registered values

A registered property with universal syntax may have the guaranteed-invalid computed value even when its registration has a nonempty initial value. A child explicitly inheriting that value must copy its absence. The old fast path skipped the declaration when the parent map lacked the name, leaving the child's initial value. The update path also ignored None.

The two-hunk repair keeps the seeded initial value only for a root element and removes the selected entry on an absent parent value. Direct inheritance continues to mark INHERITS_RESET_STYLE, including the previously skipped invalid-parent path. The standalone patch contains one Rust file and one twelve-case WPT.

## Validation

The corrected paired shared-tree macOS run has three baseline failures and nine passes in the new test, changing to twelve passes. All 28 adjacent/readiness subtests remain PASS, all five harnesses report OK and both suites end normally. The new test covers missing and cyclic parent values, inherited/reset buckets, typed invalid defaulting, direct/substituted keywords, root initial behavior and parent invalid→present→invalid changes.

Both builds exit 0, with four retained build-monitor KeyError export diagnostics each. Sources, selected test inputs and binaries remain stable within each phase. Format and lint exit 0; lint reports one ignored-WPT ESLint warning. Exact two-file patch application/reversal passes on upstream and branch snapshots. Runtime uses the shared experimental tree, not an isolated upstream checkout; unrelated cascade changes are excluded from final.patch.

The initial pair under initial-harness-error-v1 is not validation: a root-control cleanup callback returned removeProperty's string and stopped later cases. The corrected callbacks return undefined. Those failed runs remain as evidence of the test correction.

Discovery came from source inspection followed by browser reproduction. The compact formal companion separately proves the selected explicit-inherit gate/update model under initial seeding, root-parent absence, map representation and normal-return premises. It does not prove the whole cascade, concrete map implementation or invalidation scheduler. The separately reproduced substituted-inherit invalidation defect and map-iterator source lead are outside this repair.
