# Signed local CSS checkpoint

The following commit objects were signed and signature-verified in order while the native build retained its original HEAD and index. Publication waits for the owned build phase to finish; PUBLICATION.json records the later branch transition.

| Work | Signed commit |
|---|---|
| demand-model | `9a7b3b5dfa608ec5f15184b9e0089d84430ba5ca` |
| raw-attr-audit | `3958fe2e4e087ad243fa9ba9d5d7c926f689af1c` |
| used-attr-fallback-audit | `4a42780a0c1e1f6f0316236b3026fa9d045a67e5` |
| ordinary-regression-roster | `d22aabc6270a89302ef4070a4211ffdda1283fd3` |
| registered-fallback-audit | `eea3a6bdb99b45dc7f497e0ca2d73aa403b017dd` |
| single-collector | `48f5002bb1b49258c4ce4b8d511622e314529584` |
| unfinished-snapshot | `c658aea9918cc81f60af0bbf46877530b6bfed64` |
| typed-demand-runtime | `c00d7163791277854ed9be9c1e6267cd3bb51ca2` |

The Lean substitution model passes 17 audits, 16 kernel examples and six negative controls, independently replayed. It proves stability of already-settled evaluations under coherent completion, not a complete native CSS resolver or arbitrary scheduler confluence.

The raw attribute and used-fallback audits reproduce five and seven release-browser disagreements respectively, with controls. The registered fallback unit audit retains an unexpected number-control failure and an unresolved length-spec interpretation. These are investigation leads; branch reproduction and repair validation are pending. The ordinary regression roster is prepared but has not run.

The single-collector package is an uncompiled candidate with syntax and exact transport checks. Production pending source transport and joint completion remain open. The earlier separate collector is explicitly superseded. Neither proposal is activated.

The current typed-demand source patch has passed Rust compilation after correcting Atom serialization in its test bridge. The broad native build was still running when these records were signed. Twenty selected GTests (including one test with 22 resolver calls) and the four ordinary WPT files remain to run. SIGNING-STATUS.json preserves that distinction.

The unfinished-work v5 recovery snapshot captures all 129 currently modified or untracked inventoried project files in a patch against BASE.json; forward/reverse application and exact source hashes passed in an isolated index. The working tree intentionally retains these prototypes for continuation. Unrelated files and build products are excluded. Accepted native fixes remain separate commits containing only their necessary native patch and WPT.

Accepted count remains 135, numbered through fix136 with held120 excluded. The separately committed CSS Lean library is unchanged. No push, Try run or Phabricator submission.
