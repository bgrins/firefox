# Coherent A+B+D rollback repair rebased to e86

This is a source-only rebase of the existing `css-layer-cutoff-composition-probe-v1/fix-a-b-d-v1.patch` onto exact immutable commit `e86b64866cdc5e2260ba9be08c45756fd96e21bb`. It implements no C provenance repair. The old patch applied to copied Git objects with zero fuzz and no rejected hunk; only hunk positions changed in the regenerated patch. There was no conflict requiring a new semantic choice. `native.patch` contains exactly two Rust files and three unchanged WPT pages.

| Native file | Exact base SHA-256 | Candidate SHA-256 |
|---|---|---|
| `servo/components/style/applicable_declarations.rs` | `daf589d65a777c553470d60e71f5c134e919622ae440016e8349563eeb5d1c5c` | `a81f348851baca75e68de9bd35c3d02f6731dba6cc57304ee5882cc44b0cca26` |
| `servo/components/style/properties/cascade.rs` | `832d08549227e20f88f1bede253824b75b66a58b4adb2b7efc357cc52915f1f5` | `f130a3db946de1f432918f28601d03b79c2fd0b10420a8d1b88f6fd6a94baa06` |

`SOURCE-ROLES.json` includes the three fixture hashes. `base/` and `candidate/` retain exact source bodies. Neither the live source tree nor its existing untracked probes were changed. The patch's WPT additions are absent from the signed base, regardless of those existing worktree probes.

## Consumer review and limits

`CascadePriority::allows_when_reverted` retains the historical important-inline exception: tree declarations outside the style-attribute layer survive that cutoff; other priorities keep the existing comparison. Origin and Rule predicates are unchanged.

`RevertState` retains separate Origin, ordinary Layer and important-inline Layer representatives and intersects their predicates. It preserves the original priority values, replaces only a stricter representative within its family, and leaves Rule without a cutoff update. This is the same historical helper, not a new summary algorithm.

For longhands, the existing seen and cascade-flag guards still precede cutoff eligibility. The new cumulative guard occupies the old guard location, before substitution and ignored-color handling. A non-Rule rollback marks the existing fast membership set, updates its map entry, and returns. Rule returns without overwriting an earlier cutoff. Terminal seen/author flags and declaration application remain unchanged. No logical-rule source key, source pointer or declaration-buffer growth from C is introduced.

For custom properties, the eligibility guard remains before included flags, seen-name handling, registration and value processing. The rollback arm still removes the seen-name entry; non-Rule adds to the existing per-name state, while Rule retains earlier cutoffs. Registration, deferred substitution, initial/inherited handling and cycle bookkeeping retain their e86 bodies. Both consumers use the same helper. The source scan finds no other consumers requiring adaptation.

The unresolved stronger-rule revisit/cycle policy is not implemented or reinterpreted. Existing cycle tests and their metadata are untouched. Historical evidence recorded two expected cycle failures unchanged on the coherent repair; that is not a fresh current-candidate result. The `Rule => true` uniqueness limitation for logical/physical same-block declarations remains deliberately outside this patch. Full provider/evaluator/observer refinement and performance acceptance remain open as recorded by the predecessor review.

## Exact fixtures and resources

The selected fixture roster is A16 `revert-layer-important-inline-part.html`, B16 `revert-rule-preserves-earlier-rollback.html`, and D48 `revert-layer-preserves-inline-exclusion.html`. All three are byte-identical to their historical patch outputs; D48 is also identical to retained `without-c-D48.html`. The full D64 body is retained separately under `held/`. Its only difference is inclusion of `revert-rule` on the inline-value axis. `ROSTER.json` names the exact omitted16 C-boundary callbacks; it does not silently delete them from the investigation. Twelve expose the C defect in the historical no-C comparison, and four are numeric masking controls.

The two absolute `/resources/` dependencies are copied from e86 under `resources/` and pinned by `RESOURCES.json`. They are supporting resources, not extra files in the native patch. No test metadata or expected outcome was changed. Serving or staging these fixtures and observing the current baseline must precede any native candidate execution.

## Focused validation

Actual check `1e92ee` exited0. `CHECK.log` records exact base/source/reference authentication, historical and regenerated zero-fuzz forward/reverse patch equality, Rustfmt edition2024 parse success for both copied Rust files, and inert Node registration of exactly80 unique callbacks. Node does not invoke test bodies or emulate a browser. The D64/D48 one-axis identity and16 held names are checked. Temporary patch trees were removed. The initial materialization's patch-generated `.orig` was checked equal to the copied base and removed from the owned artifact.

Rustfmt parsing is not Rust typechecking, a Gecko build or execution. No native build, browser, Lean replay, general runner/owner, Git index write or canonical-state mutation occurred. This package makes no new bug-count, acceptance or landing claim. Baseline reproduction and a fresh candidate build/comparison remain pending.

Provenance and the current-spec/held-status adjudication are pinned in `REFERENCES.json`, including `css-rollback-held-leads-review-v1` seal `9335f0bf…`. The old A-only and A→B→C ordering are superseded; the coherent A+B+D unit is required before considering C.
