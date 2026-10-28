# Manual source correspondence

| Model | Captured native boundary / premise |
| --- | --- |
| Leaf.percentage / Leaf.length | map_line_height_leaf preserves Percentage→NoCalcLength::from_em and resolve_line_height_length; the latter selects CurrentStyle font, InheritedStyle line-height, and conditional text scaling. Numeric details are abstract inputs, not proven. |
| correctedMap fallback | Proposed leaf.to_computed_value(Some(context), None), with Result passed directly into resolve_map. |
| genericMap random/tree | Leaf::to_computed_value resolves RandomKey through its context computation and TreeCountingFunction through its current context, producing Number. Context input correctness is assumed. |
| oldCloningMap unresolved cases | Old mapper's catch-all clone leaves the key/tree leaf symbolic; generic canonical-value extraction cannot resolve it without context. The model compresses those stages into none. |
| referenceLeaf | Manually written interpretation for this restricted leaf subset. It is not machine-extracted CSS or Rust. |
| expression_semantics | Structural induction for a small finite unary/binary expression language with pure supplied operations. Native n-ary/math-function coverage is not established. |
| special_bases_preserved | Corrected mapping keeps integer-multiple percentages on the resolved em basis and lh on the inherited basis, rather than generic current lh. |
| old_clone_random_witness | Abstract random range1..3 at base0: corrected numeric factor1 gives10 with used font10; unresolved old key gives modeled fallback0. No PRNG proof. |
| generic_only_lh_witness | Exact ratio inherited40/em10 gives factor4; replacing the special branch with generic current70 gives7. This tests why delegation must exclude lengths. |

REFERENCES pins the actual reviewed native proposal, base, shared leaf evaluator, generic resolver and primary-spec trace/capture. The native proposal remains uninstalled/uncompiled in that historical package; this proof does not change its validation status. Three rejected controls cover old random cloning, old tree cloning and loss of the percentage special case. No claim about a complete parser or arbitrary context-independent initial validation is made.
