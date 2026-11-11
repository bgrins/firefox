# CSS keyframe group order

The reverse-assembly algorithm with a move-to-end operation produces the same
group order as retaining each key's first occurrence. `reverse_loop_order`
proves this for every finite list over any type with decidable equality, using
the standard library's `List.eraseDups` as the reference operation.

The current CSS Animations 2 contract and known bug 1778402 are traced in
`../css-css-animation-keyframe-failure-triage-20261110-v1/REPORT.md`. This proof
models the ordering step; the mapping from specification prose is reviewed
manually. It does not mechanically derive that contract from the prose.

`assemble_is_reverse_loop` connects the recursive model to an actual right-to-left
fold. `move_existing_rotation` proves that, when a key occurs only at the selected
position, filtering that key and appending it equals rotating that position to
the end. `append_new_group` covers a missing group. `unique_groups` and `membership`
establish that the loop neither duplicates nor loses groups. `earliest_filter`
and `earliest_eq_eraseDups` connect the independently expressed first-occurrence
recurrence to the standard reference operation.

For the native candidate, a key represents the already-resolved percentage,
timing function and composition tuple. The input is the sequence after stable
offset sorting. The C++ helper moves the whole existing group; its declaration
payload and ownership are outside this key-only model. Correct tuple extraction,
stable sorting, declaration precedence, move operations, pointer validity and
named-range processing require separate native source review and browser tests.
The proof does not model floating-point comparisons or establish C++ memory safety.

The previous algorithm retains a group's latest occurrence instead. The checked
counterexample `[0, 1, 2, 1]` yields the wrong relative order. This explains the
already-observed test failure; the proof did not independently discover a new bug.

Run:

```sh
python3 -B check.py --lean /path/to/lean --out /new/output/directory
```

`verification-3/report.json` records 15 kernel-checked theorem audits and three
compiling semantic mutants: preserving the old position, prepending the group,
and retaining duplicate groups. Each mutant compiles, rejects the unchanged
laws, and produces the exact expected false-proposition diagnostic for the
unchanged concrete witness. The positive witness passes first. Only the usual
Lean logical axioms are permitted; no `sorryAx` or native evaluation axiom is
accepted. Builds run in a fresh temporary directory that is removed afterward.

The first two checker attempts rejected a mismatch in the diagnostic string
expected for a false `decide` proof. Their logs are retained in `verification`
and `verification-2`; they are not successful validation runs. The final matcher
requires the complete diagnostic, including its exact trailing newline.

No canonical CSS library integration, native build or browser-fix acceptance is
claimed by this capsule.
