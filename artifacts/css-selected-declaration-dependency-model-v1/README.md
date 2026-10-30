# Dependency reads stop at the selected declaration

The new theorem is an arbitrary-list preservation rule: after declaration evaluation reaches a terminal value or a blocked evaluation, appending any lower-priority declarations cannot change the result, evaluated declarations or dependency-read trace. Rollback is not terminal: its own reads remain, eligibility is checked under its returned state, and evaluation continues. This supplies a missing connection between the existing cascade selection models and demand-driven variable evaluation.

`Selection.lean` proves eleven statements. The main `losing_suffix_irrelevant` theorem quantifies over declaration, state, value and edge types, arbitrary lists, and arbitrary deterministic eligibility/evaluation functions. `read_provenance` proves every recorded read belongs to an eligible evaluated declaration. Separate laws preserve attempted rollback reads and exclude skipped candidates. Terminal `none` also stops; invalid-at-computed-value-time is not silently treated as permission to try the next declaration. Blocked evaluation records its reads and stops pending resolution, without assuming that a later winner may be evaluated.

The concrete witness reuses the exact existing `DemandFallback.eval`, rather than adding another fallback evaluator. The first declaration reads `--ok`, whose value is `revert-layer`; the declared evaluator interprets that result as rollback to state 2. It skips declaration 1 and reaches declaration 2, whose missing primary selects `--fallback`. The trace is exactly `--ok`, `--missing`, `--fallback`: it preserves the attempted rollback read and selected fallback while excluding `--unused`, `--loser`, and every declaration after the winner. Interpreting tokens as a rollback keyword and translating state 2 into real layer/origin/rule eligibility are explicit model inputs, not proved CSS parsing rules.

An independent two-node graph enumerator detects a cycle after eager collection reads `--x` from an overridden declaration. The fixed reverse edge represents a custom value depending on its ordinary property. Selected evaluation of the earlier literal adds no forward edge, so no cycle exists. Six separately compiled false claims reject eager/selected equivalence, discarding rollback reads, including an unused fallback, treating rollback as terminal, reading a skipped candidate, and denying the eager cycle.

## Existing results reused and the remaining gap

`CustomCascade.dependency_iff` already ties custom-property dependencies to a cascaded expression, and its provenance theorem identifies a selected rule. `LayerRollback.resolve_sound` and the layer/origin trace laws already track selection through pre-tagged rollback. They do not record dependency reads from computed substitution that produces rollback. This package does not duplicate their layer/origin selection proofs. It imports the immutable demand-fallback evaluator and adds the generic evaluated-prefix invariant; the existing models are referenced by exact source hashes for this comparison.

The frozen root trace in `css-overridden-dependency-spec-trace-v1` establishes the simple literal font-size winner scenario from cascade and substitution rules. Its declared scope excludes a proof of the full Rust repair. This model likewise does not formalize the complete CSS sorting, `allows_when_reverted`, Appearance eligibility, forced-color adjustment, Tarjan lowlinks, monotonic cache effects or generated scheduling. Correct evaluator and eligibility behavior, stable evaluation inputs and demand-selected reference reporting remain native correspondence obligations. The theorem does not authorize freezing eligibility before a reached Appearance input or ignoring reads from an evaluated variable-produced rollback candidate.

The native proposal V2 is only a frozen comparison point. It stages selection and commits after SCC closure; this Lean scan neither validates that staging nor proves the inherited Zoom/active-custom scheduling boundary safe. No Rust compilation, browser run, native refinement, normative cycle-policy proof or accepted-fix increment is claimed here.

## Actual verification

Pinned Lean 4.35.0-rc4 compiled five existing source dependencies, the unchanged demand evaluator and the new source in a fresh owned scratch. All eleven axiom audits use only `propext` and, for read provenance, `Quot.sound`; all six false controls failed because their propositions are false. The successful source retains three harmless unused-simp-argument warnings. `ACTUAL-LEAN-TERMINAL.json` and `run3` preserve the actual success, command logs and source copy. Two earlier proof/elaboration failures remain in `run1` and `run2`; all three scratch directories were removed. No canonical Lean modules or native source files were changed.

Replay from the repository root, with a new output directory name:

```
python3 -I -S -B artifacts/css-selected-declaration-dependency-model-v1/replay.py run4
```
