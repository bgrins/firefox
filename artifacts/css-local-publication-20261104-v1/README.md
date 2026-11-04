# Local publication record — November 4

All listed commits were created locally with the configured SSH signer; no push or external submission occurred.

| Commit | Role |
| --- | --- |
| 92bb75455480 | Recovery and current roadmap |
| dfddd364baf6 | ArcSlice research predecessor |
| 836b5a688284 | Empty ArcSlice alignment repair and Rust regression, exactly three files |
| 407a423cb4e6b | Cumulative rollback research predecessor |
| e63fc6b1892b | Cumulative rollback repair and WPT, exactly two Rust files and three tests |
| 4291dff2735a | Same-rule research and comparisons; no production C change |

Each completed operation has a recipe, exact selected payload hashes, log and RESULT.json. The driver checks staged blob identities, exact commit scope, signature presence and cleanup. This records configured signing and embedded signatures, not a new independent cryptographic trust-policy verification.

The browser catalogue now has 162 repair entries, including held #160 and excluding #120. #163 is the coherent cumulative rollback delivery, whose interacting mechanisms cannot be separated into the historical small patches without known regressions. ArcSlice is recorded separately as a generic-library repair with no established browser-reachable over-aligned caller.

The same-rule diagnostic fixed all 28 failing callbacks in its 190-case comparison and retained controls, but remains unlanded pending performance review. The benchmark is prepared and syntax-checked only. The old D64 probe bytes remain preserved; #163 commits the tested D48 file.

The earlier failed signing records remain valid history. The first retry in css-recovery-roadmap-signing-retry-v1 stopped before signing because the research path was ignored; v2 used explicit force-staging of that path and produced92bb75455480. No signer bypass was used.
