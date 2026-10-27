# Fix 121 signed-history rewrite: HOLD

The disabled v1 source follows the fold-plan-v2 tree construction, but its publication success gate can accept the wrong checked-out HEAD. Preserve this review and v1 unchanged; review the author's immutable correction before activation.

## Required correction

`branch = symbolic-ref HEAD` is checked only before the 37 signatures. The prepublication epoch helper checks the HEAD commit, not its symbolic target. If HEAD switches to another branch pointing at the same carrier, that gate still passes. The transaction updates the originally captured branch. The success tail then accepts whatever HEAD `index_state` returns, replaces the epoch's semantic HEAD with it, and reports VERIFIED without requiring the new tip or original branch. The final tree is equal to the carrier, so all raw/semantic index and working-body checks can pass in this case.

`reproduce.py` executes the actual eight-statement success tail against inert index/guard boundaries. It returns VERIFIED with actual HEAD `cccc…` and declared new tip `dddd…`. This is an admission/control-flow reproduction, not a live Git race or ref transaction. Actual replay tool1476ef exited0; no Git subprocess or live state read occurred.

Require the exact symbolic HEAD before publication and exact new HEAD plus the same symbolic target afterward. If the available Git supports atomic symref verification, include HEAD's target in the same publication transaction; otherwise state the remaining no-concurrent-checkout premise explicitly. Postpublication failure must remain FAILED with actual-head observation and no blind rollback/retry.

## Reviewed scope that otherwise agrees

The source authenticates 37 original commit objects and the exact linear parent chain, and verifies their signatures plus the carrier using the configured public SSH key. It requires the carrier on the fixed tip, exact new research additions plus the one metadata correction, hashes/modes, and a fresh root-admitted post-carrier epoch. Existing 39 promoted paths, all sequence rows and all 13 active fix mappings exactly equal the sealed plan. The preservation helper explicitly requires empty main staging and checks full guarded source/binary/research/identity maps, scoped native inventory and both indexes.

A new exclusive backup ref precedes replacement construction. Each temporary index starts from its own original tree; only selected research blobs and the exact metadata block removal are overlaid. Complete per-tree changed-path sets and selected modes/bodies are checked. The first research commit leaves metadata unchanged; every later tree removes its own single block, preserving the later steps/cubic changes. New signatures preserve author/date/message and verified parent/tree. Final tree equality to the carrier plus the 37-commit count precede publication. The real index/worktree have no writer in this script.

The CAS names the expected carrier and verifies the backup in one ref transaction. Preservation runs before and after publication; raw bytes are compared, not inferred from semantics. Failure receipts retain completed attempts and actual HEAD; a failure during or immediately after a ref subprocess can leave publication status uncertain until the observed actual HEAD is inspected. The script must never automatically resume or reset that state. Late receipt publication failure is a failed outer run, not a successful rewrite.

The proposed mapping uses verified IDs for every active field in its fixed 13 rows, including fix133 research_commit and fix134 research_commit/shared_prior_research. It writes an artifact proposal only, not live ledgers. Historical acceptance/signing receipts, previous/history fields and old signatures remain immutable evidence. There is no new fix or formal credit.

## Validation and limits

All draft payloads and fold-plan payloads authenticated. The author's inert checker was independently replayed: 37 exact metadata transforms, malformed selection/block gates, ambient overrides, disabled refusal, exclusive ATTEMPT and current-field coverage. Its subprocess boundary forbids Git. These checks do not execute signing, object/tree construction, CAS or live preservation. Full source/helper reads support the above assessment; root must bind actual validation/root/peer receipts, additional selection and fresh epoch before any live action. No native, canonical, index, ledger, signer or Git mutation occurred in this review.
