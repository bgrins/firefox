# Independent order-model source review

Reviewed the parent-owned `css-keyframe-group-order-lean-20261110-v1/GroupOrderModel.lean` and `GroupOrder.lean`; exact inputs are bound in `MODEL-INPUTS.json`. This review did not rerun Lean. The parent's final receipt reports 15 theorem audits and three compiled semantic mutants rejected by unchanged laws and the exact negative-witness diagnostic. Those outcomes remain the parent's execution evidence.

`earliest_eq_eraseDups` identifies the hand-written earliest-order function with Std's `List.eraseDups`. `assemble_is_reverse_loop` connects recursive processing to `keys.reverse.foldl moveLast []`; `reverse_loop_order` identifies the final reversal with earliest-occurrence deduplication. This matches the pinned Rust percentage-loop traversal. The old-order counterexample uses `A, B, C, B`, the existing WPT's decisive pattern.

`moveLast` removes every occurrence of a key, whereas C++ rotates one matching frame. The native unique-group invariant is necessary: `move_existing_rotation` states the absent-before/absent-after premises and produces `before ++ after ++ [key]`; `append_new_group` covers an unmatched key. Final uniqueness and membership are proved. The native helper starts with an empty array and adds only an unmatched group, providing an inductive uniqueness argument assuming matcher equality is an equivalence relation on admitted keys.

Integration premises outside Lean:

- Keys represent native percentage/easing/composition equality, including offset conversion and timing equality. Generic `DecidableEq` does not establish native equality-to-spec correspondence, default `auto` equivalence, or numeric representation behavior.
- Input keys are already stably sorted percentage steps. Sorting/deduplication commutation is not proved; the source argument relies on stable source order within each offset and matching keys sharing that offset.
- Raw-pointer validity, the same-offset suffix, move semantics, no surviving element borrowers, declaration references and the returned tail pointer are source-review obligations.
- Properties and declaration precedence are absent. Whole-frame payload preservation and logical-to-physical mapping require native review and WPT checks.
- Named ranges, generated endpoints, CSSOM freshness, rendering and performance are outside the model.

No source-level blocker was found under these premises. The universal abstract ordering result does not replace the build, browser controls, ownership review or declaration-winner gates.
