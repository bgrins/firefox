# Definition-stage controls

`Controls.lean` evaluates seven observations; `CONTROL-EXPECTED.txt` is the exact independently stated expected output, checked by the replay driver. These evaluations are diagnostics, not proofs of universal obligations.

| Row | Input/observation | Expected meaning |
| --- | --- | --- |
| 1 | Two equal-identity normal seeds; providers [-1,5] then [123,5] | First pass freezes slot 0; the later 123 cannot overwrite it. Final ordered sizes are 0,5 with count2 and no fallback. |
| 2 | Strut plus min-clamped/max-clamped/zero-shrink-factor seeds | Shrink early-freezes slots0/1/3; grow slots0/2. |
| 3 | Already-frozen nonempty strut, info off/on | Immediate finish without info; one harmless pass with info retains the full item state. |
| 4 | Empty seeds both info modes; wrong provider length | Both empty starts finish; wrong length returns none rather than truncating the list. |
| 5 | Arbitrary final-index invocation with two active items and only one min violation | The actual fallback branch executes. No claim that this invocation has a valid generated History. |
| 6 | Corrupted frozenCount2 with two unfrozen items | Source-shaped counter exits skip both items; it is essential to derive count agreement, not assume this executable repairs it. |
| 7 | Large signed delta at ±2^40 | Preferred-range clamp is ±(2^30−1), distinct from full int32 bounds. |

`Witness.lean` separately proves the admitted two-seed domain, a final History built from initial and two real step constructors, and its joint result/freshness. It imports only the target, not a universal target theorem or previous violation proof. Those three finite proofs may use only standard logical axioms. The remaining general target and other joint-target conjuncts are still obligations for a separately authorized campaign.
