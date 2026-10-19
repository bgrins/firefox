# Scoped registered inherit repair proof

## Result

A compact Lean component proves the selected explicit-inherit gate and publication update correct under stated source-representation premises. The independent expected value is the registered computed initial for a root and the actual parent's selected optional value for a nonroot. Guaranteed-invalid absence is preserved rather than replaced with a seeded initial.

The seventeen audited results cover the full pointwise store, other names/bucket, arbitrary other flags, preservation of an incoming reset-inheritance bit, exact outgoing bit, original counterexample, independent necessity of both changed sites, root-overcorrection witness and the root/no-initial branch. This is a conditional source-bound model checkpoint, not a universal native cascade/cache/scheduler theorem. No payload Eq or numerical-fidelity assumption is used; keys alone have DecidableEq.

## Actual model and premises

`gate` follows the native explicit-inherit projection, including its early inherited-property skip and existing-value Option split. The original present-current branch checks whether the parent reset entry is present. The corrected branch skips root. `update` sets the reset-inheritance bit before reading/cloning the parent reset entry; the original preserves storage on None and the candidate removes it. `run` composes the actual optimization with that update.

`Ready` states the selected entry is seeded as the ordinary cascade prepares it, and the root's parent reset map is empty. Declaration selection, root/registration identity and provider readiness are explicit admissions. The model starts with arbitrary other entries and incoming flags; it does not silently replace the whole map with a singleton. `corrected_store` gives a pointwise independent result for every bucket/key. `other_flags` and `run_other` preserve the frame for both original and candidate controls, including partially repaired variants.

The exact corrected INHERITS_RESET_STYLE result is incoming OR `!inherited && (!root || initial.isNone)`. Thus every admitted nonroot reset-property inheritance marks the dependency, even when both entries are absent. A root with a present initial retains the incoming bit; a root with no initial executes the existing update branch and marks it. This intentionally models implementation behavior rather than claiming the bit is set only for semantically necessary dependencies.

Full source correspondence and limitations are in SOURCE-MAPPING.md and SCOPE.md. Twelve complete native definitions are retained and reextracted. The exact original/candidate files and patch are preserved. Artifact patch application and reversal must reproduce exact bytes.

## Counterexamples and mutation gates

A nonroot reset property with computed initial some7, parent None and seeded current some7 is Ready. The original returns some7 despite expected None. Fixing only the gate still leaves some7 because the update ignores None. Fixing only the update leaves some7 because the gate skips it. The corrected combination returns None. A root with initial some7 and empty parent demonstrates why blindly executing the update is an overcorrection; the corrected root guard preserves some7.

Four semantic mutants each change one model definition: original absent-parent gate, dropped None removal, dropped root guard and dropped reset dependency bit. The replay first compiles the unchanged definition-only module and accepts its concrete witness. It then compiles the mutated definitions successfully and requires the same kernel `decide` witness to fail because its proposition is false. Syntax/import/typeclass failures are rejected as mutation evidence. These are compiled Lean model mutants, not compiled native Rust mutants or universal native compiler correspondence.

## Evidence and boundaries

The source proposal capsule was fully authenticated before copying: 26 entries, FREEZE612c60bb97962e1249c6460f4bb504b29ccf40fa580d4952a8a10361a1df8c01. INPUT-PROVENANCE.json records exact copies. The source-only replay checks the entire closed inventory before loading source_check.py or invoking Lean. The theorem audit is an exact named seventeen-result roster with only standard axioms allowed.

Root's corrected runtime context records three new failures improving to twelve PASS, 28 adjacent PASS unchanged, five harness OK. These are root's separate paired-build results; this companion does not rerun or independently replace its native/WPT review. The earlier producer v2/root test had a cleanup callback returning a string and caused a harness error; root preserved that bad-harness attempt and corrected the final test. This proof does not infer candidate acceptance from the incomplete earlier run. Final corrected test hash is recorded in runtime-context/CANDIDATE-PINS.json.

The scoped model proves neither full style/cache freshness nor all arbitrary public cascade histories. It does not implement parser semantics, actual persistent maps/COW/heap, registration replacement, pseudo construction, clone/taint internals, compiler behavior or global flag API semantics. Syntactic initial-value descriptor storage and already accepted fix71 are unchanged. The source/consumer premises must remain visible if this component is later composed into broader formal milestones.

No new native build targets were created. Root retains independent formal review, final native/WPT acceptance and commits.
