# Claimed result inventory

There are 31 audited named results, separated as follows:

- 12 unchanged OffsetEncoding results: no explicit reserved code; exact auto classification; explicit/auto decode; Option round-trip; nonreserved preservation; lower/upper range; maximum one-unit change; change iff endpoint alias; monotonicity; signed32 result; and the original alias counterexample.
- 12 OffsetSource results: numeric refinement for new/old observations; requested-side single query; auto skipping numeric resolution; explicit forwarding of the basis exactly once; exact auto-code classification; explicit decode; signed32 result; complete nonalias-observation preservation; explicit one-unit bound; a counterexample outside the bounded numeric premise; and signed32-safe constant subtraction.
- Five ModelMutants results: concrete kernel witnesses for auto-branch, max/min, two-unit, negative-value and selected-side mutations. They establish sensitivity to those mutations, not universal robustness.
- Two generated Calibration results: the entire 236-input original and repaired observation tables agree with the independent boundary oracle, by kernel reduction. The native comparison and compiled Lean driver add concrete execution checks; neither replaces the stated provider assumptions.

The first two groups quantify over mathematical inputs with their actual displayed premises. The final two groups are finite results. Read the complete theorem signatures in lean/ and generated Calibration.lean, not merely these labels. AUDITS.json specifies the closed declaration roster and generated additions. A fresh audit checks all claimed dependencies against the three ordinary permitted Lean axioms.
