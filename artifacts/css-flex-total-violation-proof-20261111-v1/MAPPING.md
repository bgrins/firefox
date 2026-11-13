# Target and proof mapping

| Frozen obligation | Proof | Scope |
| --- | --- | --- |
| DifferenceTarget | Bounds.difference_target | min-first clamp, exact difference and signed64 range |
| PrefixTarget | Bounds.prefix_target | summand bounds times acquired count, every prefix |
| FoldTarget | Fold.fold_target | each subtraction and next sum admitted; result equals independent list sum |
| SelectionTarget | Selection.selection_target | actual branch comparisons equal sign-of-adjustment selection in original order |
| ProgressTarget | Selection.progress_target | nonzero total supplies same-sign summand; zero selects all |
| CompatibilityTarget | Fold.compatibility_target | successful fully checked32 expression sequence equals wide result |
| WitnessTarget | Cases.witness_target | jointly acquired aggregate/sign and subtraction-domain witnesses |
| UniversalTarget | Laws.universal_target | conjunction of all seven unchanged obligations |

Model.lean and Target.lean are byte-identical copies from approved target V2. TRANSPORT.json and TARGET-INPUTS.json bind exact origins. No definition, proposition, import or namespace change was made to those copies. New proof modules use Std through that target; no previous arithmetic theorem module is needed.

Controls contains sum-only and difference-only folds, wrapped sign selection and reversed output. Each wrong behavior compiles and has a theorem negating its intended universal property. Six separate false-claim files must produce exactly one ordinary Lean error with exit1; elaboration failure by itself is not the semantic evidence. Cases supplies direct positive/negative/empty/mixed witness proofs independently of Laws.

The replay checker is the accepted gap-proof checker with only its semantic-refusal import changed from FlexGap.Controls to FlexViolation.Controls. CHECKER-DELTA.patch records that single change. It authenticates source/transport/tool and Stdlib pins before and after execution, requires exact audit names/no duplicates/standard-only axioms, runs one Lean process at a time with4GiB/180s bounds, and removes only owned scratch after recorded process-group absence. Unexpected cleanup inspection failures retain scratch. This is process-group monitoring, not a hostile-detached-descendant guarantee.
