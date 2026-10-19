# Zero-tab companion v2: producer results

All four independent v1 findings have implementations and passing producer
gates. Independent v2 review remains required. This report does not accept the
repair or alter the accepted-patch count.

## Changes from frozen v1

1. The direct checker authenticates all replay helpers before importing them.
   A corrupted helper containing a marker-file side effect is rejected before
   executing that side effect.
2. 432 numeric negative resolved-width cases execute both full intrinsic loops
   (216 each). The numeric tab size remains nonnegative; negative letter spacing
   makes the computed width negative. Complete raw states/provider traces agree
   with the independent Python oracle. Separate checks verify repeated width
   resolution, original/candidate preservation, and a nonpositive-guard mutation
   witness in each caller.
3. 120 defined saturation cases execute both loops (60 each), covering cap and
   infinity branches. A separate validator checks every relevant batch and
   conversion, including signed-integer headroom for the mutants. Independently
   removing each loop's saturation produces successful semantic counterexamples.
   These rows are excluded from the unsaturated Lean bridge.
4. `windowValid`, `providerAgrees`, and `admissiblePrefixes` state the model's
   window, provider and representability premises explicitly. Two new theorems
   establish the final representable bound and zero-width agreement with the
   measured provider range and normal caller model. The unconditional algebraic
   lemmas remain. These are model applicability statements, not universal C++
   refinement or proof that real renderer providers satisfy the premises.

## Executed gates

Preparation session 23824 and clean source-only session 56319 both exited 0.
Their complete summaries are byte-identical:
`2176ea22f50dd88ffe40a415d877bf93ac04e634286571e36e5dc9f7298c3358`.

- 2,931 cases per original/candidate and each of twelve native semantic mutants.
  All fourteen variants compile and execute successfully with undefined-behavior
  and float-cast sanitizers, assertions and warnings-as-errors.
- 1,895 complete native/Lean records per original/candidate variant agree.
- All 35 theorem declarations pass axiom audit with only standard foundations.
- Six Lean mutations have both rejected proofs and successful, differing
  theorem-elided executable witnesses.
- All 1,690 nonzero records are unchanged; 367 zero-width records differ.
- Twenty computational source pins and 29 exact extraction fragments are checked.
  The latter are bodies, declarations, members and accessors, not 29 functions.
- The source-only package contains 31 listed files plus its manifest. Final
  source-only integrity verification passes. The final verifier gained external
  evidence checks after the full replay; all twenty computational inputs are
  identical to that replay. See `EXECUTION-v2.json` for the exact distinction.

`preparation-v3/BOUNDARIES.json` retains per-caller counts and semantic witness
IDs. Full public state, spacing/cache records and the declared provider event
inventory are compared. Pure getters/classification remain supplied premises.

## Preserved limitations and history

The exact native repair remains the three-line zero-width guard, with no further
Gecko or WPT changes. The shared helper's positive-width zero-font defect and
tiny-positive policy remain separate. There is no ASan, IEEE, pointer-lifetime,
font-shaping, scheduling or complete-renderer proof claim.

V1 remains frozen and unaccepted against the full scope. Two early v2 boundary
preparations were rejected before compilation because a generated case did not
actually saturate. The first Lean preparation used a reserved identifier and
failed compilation. Their logs remain intact; none counts as a successful gate.

The source-only replay output lives in a separate artifact directory. Its entire
file set, the source-only package, and the v1 review/approval evidence are pinned
by `EXTERNAL-EVIDENCE-v2.json`. The default verifier checks that closure before
reporting success. Historical evidence is not converted into current binary pins.
