# Focused Round reconstruction/projection analysis

Four all-input SMT obligations are UNSAT: both nearest-distance comparisons, small-step native-bound projection, and the stronger directed enclosure of both exact bounds including reflected negative endpoints. Three SAT checks retain a wrong tie adapter, omitted small-step premise and actual nonvacuity witness. No candidate-result counterexample was found in these obligations. The earlier4,151,200 strategy executions were not repeated.

The split b<a/2^28 versus a<=2^28*b closes the previously uninstantiated numerical interval conditionally on exact truncating remainder and the stated IEEE bridges. Small steps project both exact and reconstructed bounds back to the input. The complement applies the existing bounded-significand result with binade=a, then the new distance lemmas justify nearest selection. ARGUMENT.md explicitly enumerates zero/exact multiples, larger-than-input steps, subnormals, signed zero, threshold equality, nearest ties and overflow.

Z3 4.16.0, SHA537a502af2f4013a8e887beebe525a0dae84918a61ff545991e36dfda07ed6d7, ran sequentially with one thread,45-second solver and55-second outer limits. All seven final queries exited0; slowest11.64seconds. No SMT certificate was imported into Lean. results/ contains the final seven-query evidence. The earlier first positive log and external four-query replay remain historical. prepare.py regenerates exact input hashes; replay.py writes to a fresh directory and fails if a result becomes unknown or changes.

The tie SAT model is independently checked as b=16458855/8388608,r=b/2; replacing< with<= chooses the wrong tie side. Omitting the small-step premise admits a=1,b=3/4,r=1/4, an actual q=1 remainder relation whose bounds do not both project to1. Nonvacuity uses retained a=1,b=5*2^-149,r=2*2^-149. None is a counterexample to the proposed repair.

This adds quantified evidence for specific obligations, not a full native runtime proof. Mathematical/SMT composition remains manually reviewed, actual Rust fmod and compiler refinement remain external, and no native/browser acceptance is granted. Imported capacity/decoder results receive no duplicate credit; no canonical registration, source/index/browser/build mutation or compiler product was created. Source discovery remains the original quotient-rounding analysis, not a new defect claim.

Replay:

```
python3 -B -I -S artifacts/css-round-reconstruction-projection-analysis-v1/replay.py --output /absolute/absent/reviewer-directory
```

Primary semantics consulted2026-10-24: [SMT-LIB FloatingPoint](https://smt-lib.org/theories-FloatingPoint.shtml) defines binary formats, directed/nearest modes and nearest-quotient remainder. [Rust numeric casts](https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast) specifies exact widening and nearest-even narrowing with signed infinity on overflow. These contracts inform external correspondence premises, not a verification of a particular compiler/hardware implementation.
