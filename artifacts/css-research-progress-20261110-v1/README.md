# CSS verification progress

Fourteen research commits have verified SSH signatures. No production repair was applied. Existing unrelated untracked files were preserved.

| Commit | Research |
| --- | --- |
| `05ffebd5c6b4` | Model transient animation rule recascading |
| `36e5c3428576` | Record recascade enum failure and revised setup |
| `cee657642cfd` | Diagnose scroll geometry in recascade tests |
| `5068cc54137a` | Validate bounded transient recascade helper |
| `41feaff0b4a3` | Investigate null-progress transition origin selection |
| `d927255cf55e` | Prove conditional transition origin properties |
| `bc03d5b6bd65` | Record a held transition origin-filtering proposal |
| `66a5507e0e70` | Record inconclusive WebKit timing comparison |
| `f1b7ff6318b9` | Prepare combined animation composition diagnostics |
| `8b615e441ce2` | Demonstrate pending animation sampling time divergence |
| `c7f9ff8bfac0` | Map public pseudo style provider integration requirements |
| `0099b41e0ae3` | Prove bounded CSS unordered grammar semantics |
| `b5ac99820c4f` | Record composed animation recascade observations |
| `e8fac22eb2d2` | Compare proved text-transform grammar with browser parsing |

The composed experiment passed119hard checks plus208query and100recascade checks;130WPT records were unchanged. Three interpretation probes failed as predicted. This is a completed investigation, not an all-pass test or production repair. Full restoration was independently verified.

The pending-time witness passed47setup checks: ordinary progress stayed null while the pending animation produced20px; three controls stayed80px. This refutes the held filtering proposal’s unrestricted timing premise. Its native patch was not run.

The restricted unordered grammar proof passed independent replay of69audits and semantic mutations. Firefox matched1555normalized text-transform inputs through two APIs,3110observations, with38accepted sequences and no mismatches. This is bounded browser evidence, not a native implementation proof.

Next: review standalone grammar integration and resolve provider-value spec oracles before public missing-pseudo integration. Public CSSOM/debug gates and the protected Linux comparator run remain open.
