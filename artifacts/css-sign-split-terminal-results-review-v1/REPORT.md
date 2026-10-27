# Sign pair terminal results and restoration

Scoped GO for the recorded comparison and restoration. The evidence supports separate scoped acceptance of raw transport, followed by Sign with its explicit raw-transport prerequisite. This review assigns no fix numbers and makes no installed-candidate claim: the original stack was restored.

| Phase | All 1,037 subtests | Landing 19 |
|---|---|---|
| HEAD90 baseline | 996 PASS / 41 FAIL | 8 PASS / 11 FAIL |
| Raw transport only | 1,002 PASS / 35 FAIL | 14 PASS / 5 FAIL |
| Raw plus Sign | 1,007 PASS / 30 FAIL | 19 PASS |

All three phases have 13 OK harnesses. Raw transport repairs six own failures and passes all eight own cases; combined repairs five further Sign failures and passes all eleven Sign cases plus all eight raw cases. Every baseline PASS and exact retained failure is preserved. Combined additionally preserves every raw-only PASS and exact retained failure. All 1,018 existing controls remain unchanged: 988 PASS and 30 FAIL. No metadata, oracle or tolerance was relaxed.

Authenticated every payload in the runtime, bound checker, prior phase review and reviewed checker draft. The bound checker changes only readiness, actual session exit and terminal STATE hash. Its execution receipt records checker 24470 exit 0 and campaign 80904 exit 0. The genuine root receipt copied into the runtime is byte-identical to the checker output. REFERENCES.json explicitly pins both the full runtime FILES manifest and its ROOT-FINAL-CHECK.json.

Rejoined all 35 completed-file/log hashes from the phase-only capture and the exact completed phase-state projection. Replayed the reviewed pure raw parser, phase-source/build/binary joins and both semantic comparisons against the sealed terminal archive. Each phase has exactly HEAD90 plus its selected zero/three/four candidate paths, stable across build, and 497 complete test roles. The earlier independent phase recount remains the primary separately implemented outcome cross-check; this terminal replay reuses the reviewed parser rather than claiming a new independent implementation.

BEFORE equals FINAL and the bound original snapshot. All 67 source pins match; the 40 saved original bodies authenticate and exactly cover the 36 original differences plus the candidate union. The semantic index snapshot retains HEAD, complete staged-entry and cached-diff hashes and the exact 925-path roster. All 11 installed test body/inode records agree with the prior installation. The 427 resource roles combine with sources and rebuilt binaries into exactly 496 final roles, retaining the old Sign fixture's absent role. Both temporary fixtures and source temporary cleanup are corroborated by the root checker. Terminal state records restore build 0, restored true, no recovery errors, and no native acceptance.

Restored binary hashes are Firefox `8f8e003a7a49a79128d7132b2ee09eea3f883402dab85bfc667f6dec6a88a675` and XUL `4e254e4ef0921114ec7f1d3ff374c27edc888137368a2d70fdc7a4cca65c12d1`. These rebuilt roles are distinct from historical phase binary roles; identical original binary bytes are not required or claimed.

This is artifact-only corroboration. The authenticated root checker performed the live source/resource/binary, native inventory, semantic index, inode and absence checks; this review does not repeat live reads or a 925-blob loop. Process exit is joined to the root execution receipt, not independently observed by this reviewer. I authored the final checker and some precursor policy; the review discloses that overlap and relies on its independently reviewed checker plus the separately authored phase recount. No native/index/browser/build operation occurred here.
