# Independent A+B+D delivery review

The selected two-Rust-file/three-WPT patch is a coherent local delivery. No additional concrete correctness defect was found in this bounded source review. This is not exhaustive cascade verification or clean-upstream runtime validation. Keep C's source-block identity repair and cycle/revisit semantics separate.

## Source and prerequisite boundary

`INPUTS.json` records that both affected current HEAD (`a6f39620516a4cf76a5dbf5208960adc79068cf1`) and restored live Rust bodies exactly equal the selected e86 delivery bases. The actual native run's `BUILT.json` records the selected candidate hashes. The three new WPT paths are absent from HEAD. A/B live tests match delivery; live D64 differs from selected, tested D48. Publish the delivery bytes, not an indiscriminate staging of the current WPT paths.

A newer retained pre-project ancestor exists: `976279105b2e78b8666a959eb3f25c9176cefaf8` (2026-10-14), immediately before the first local Bloom experiment. The full five-file patch passes source-only `git apply --check --verbose` on copies of that ancestor, with cascade hunk offsets only. `ANCESTOR.json` and `ancestor-apply.log` retain identities and results; Git discovery was bounded outside the live repository. The old local origin/main merge-base (2026-03-17) failure therefore does not establish a dependency on project repairs. Historical STANDALONE-A/B checks used already-local 32226/11482 revisions and are not independent upstream evidence. No current upstream fetch, standalone build, or browser execution on the retained ancestor was performed.

The successful actual build contains earlier branch repairs and the separate three-file ArcSlice working patch. No direct ArcSlice dependency appears in these changes, but this is combined-branch runtime evidence. Fresh upstream application/build still needs checking before external landing.

## Behavior and cost

`CascadePriority::allows_when_reverted` preserves tree declarations outside the style-attribute layer when rolling back an important inline declaration. `RevertState` keeps origin, ordinary layer, and important-inline exclusions separately and intersects their eligibility predicates. Each family retains its tighter representative; Rule adds no exclusion and no longer erases earlier ones. Longhand and custom-property consumers share this helper. Registration, substitution, cycle bookkeeping and existing declaration-provider paths remain otherwise unchanged. No complete provider-order or CSS-spec correctness claim follows from the represented-state Lean proof.

`RevertState` has no internal allocation. It increases the value size in existing rollback hash maps and checks up to three predicates per gated declaration. The ordinary longhand fast membership guard remains; custom properties already performed a map lookup. Rule-only cases can avoid the former map insertion/name clone. Likely cost is concentrated in rollback-heavy cascades, especially many properties through `all`; exact bucket sizes and runtime effects were not measured. There is no evidence here of a general per-element allocation regression or performance neutrality.

## Tests and remaining limits

Actual baseline74PASS/6FAIL becomes candidate80PASS with all prior passes preserved. Existing controls remain5PASS/2FAIL with three harnessOK and crashPASS; supplemental raw audit passes and independent restoration audit confirms closure. Runs explicitly enable `layout.css.revert-rule.enabled`; they do not establish release-default exposure.

A/B callbacks assert the longhand before the custom property. Candidate success executes both assertions, but baseline longhand failures prevent observing the custom assertions in those rows. Split those assertions into independent callbacks when strengthening coverage; do not claim these runs independently reproduced both consumer regressions. Existing two cycle-control failures likewise stop at their first assertion. D48 supplies necessary cumulative-exclusion coverage; its held sixteen D64 rows belong to C's boundary. Six repaired callbacks are not six independently fixed bugs.

Recommend the exact coherent A+B+D delivery with its three tests, with research/proofs/docs in a preceding commit. Do not label shared state as a behavior-neutral prerequisite or split out historically regressing partial repairs merely for commit cosmetics. Signing/publication remains the parent's separate step.
