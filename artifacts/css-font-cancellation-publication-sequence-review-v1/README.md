# Existing local publication sequence after V127

The two sealed publishers fit the planned ordering **signed V127 research → font-unit native commit → selective cancellation native commit**. No successor driver is currently needed. All63 direct reference hashes still match; both packages' complete payloads are already selected exactly in V127. Their four install/runtime destination directories were absent at the read-only check552a9e. Live source, canonical state, test-path absence and signing availability were not rechecked here; the actual publishers enforce them immediately before mutation.

No newly stale static pins were found. The new trace builds and raw-refresh epochs do not replace the historical validated evidence bound by these publishers. They do require a fresh post-restoration research capture and successful actual V127 receipt. Historical captures, failedV126/V125 receipts, and a proposed research head cannot satisfy that requirement.

## Root sequence

Finish actual ten-role restoration/audit and final raw refresh, finalize V127's bounded selection/current binding, then use its normal check/signing lifecycle. Both publisher packages must remain in that signed tree. A real successful `artifacts/css-research-checkpoint-20261103-v127/result.json` has the `head` and `signature_verified` fields the font publisher requires. Confirm the actual signer succeeds; this note does not retry/bypass past failures.

Run these existing scripts serially, with normal signing and the actual receipt hashes substituted only after success. All commands are unexecuted here.

```sh
python3 -I -S -B artifacts/css-keyframe-font-unit-publication-v1/publish.py font-units install --manifest 45eef448b49197690b9543236fd5f60129948ed57b3fac32fb54bd1aa1d6dcb1 --predecessor artifacts/css-research-checkpoint-20261103-v127/result.json --predecessor-sha256 <actual-successful-V127-result-sha256> --pair-binding artifacts/css-keyframe-font-unit-publication-v1/PAIR-BINDING.json --pair-binding-sha256 f49bd699dbb9dd96c970c17d7c3f050c948e0ed95c920cb339deeba31ba6f145
python3 -I -S -B artifacts/css-keyframe-font-unit-publication-v1/publish.py font-units delivery --manifest 45eef448b49197690b9543236fd5f60129948ed57b3fac32fb54bd1aa1d6dcb1
python3 -I -S -B artifacts/css-keyframe-font-unit-publication-v1/publish.py font-units commit --manifest 45eef448b49197690b9543236fd5f60129948ed57b3fac32fb54bd1aa1d6dcb1
```

After actual font COMMIT-RESULT success and signature verification:

```sh
python3 -I -S -B artifacts/css-selective-cancellation-after-font-publication-v1/publish.py selective-cancellation install --manifest bbd0d3c553fd5d76e35f5ceead1c2a258870f9267e07483e5e7c433c24237bd4 --predecessor artifacts/css-keyframe-font-unit-publication-font-units-runtime-1/COMMIT-RESULT.json --predecessor-sha256 <actual-signed-font-COMMIT-RESULT-sha256> --pair-binding artifacts/css-selective-cancellation-after-font-publication-v1/PAIR-BINDING.json --pair-binding-sha256 c886bb4026ddce68f1c797c4e419c307ebc209c07b5ac9cc6a84b5e06350a414
python3 -I -S -B artifacts/css-selective-cancellation-after-font-publication-v1/publish.py selective-cancellation delivery --manifest bbd0d3c553fd5d76e35f5ceead1c2a258870f9267e07483e5e7c433c24237bd4
python3 -I -S -B artifacts/css-selective-cancellation-after-font-publication-v1/publish.py selective-cancellation commit --manifest bbd0d3c553fd5d76e35f5ceead1c2a258870f9267e07483e5e7c433c24237bd4
```

Delivery and commit deliberately take no predecessor/pair arguments; they authenticate the generated installation owner and retained bindings. Each install/commit call captures its own current state through the existing verifier. No separate new rich-capture adapter is needed between these two native commits. Do not manually enable the sealed template policies or edit their PAIR-BINDING files. The cancellation publisher fills its copy's null font receipt only during install.

## Exact preimages and limits

Font publication requires e86 data.rs6a7df6 and traversal.rs736920 content pins, absent installed identities/ownership for those two roles, actual matching HEAD bytes/inodes, and absence of the new root-font-unit-invalidation.html path. It creates only those two Rust changes and that14-case WPT. The native61 evidence remains12 improvements/49 preserved/five endings. Its message is `No bug - Refresh animated font-relative values after ancestor font changes. r?#firefox-style-system-reviewers`.

Selective publication requires the immediate signed sole-parent font commit with exactly those three paths/blobs; its prior research ancestry from e86 must be artifact-only. Traversal now has font hash402165 and an installed identity; glue remains canonical83cc with installed identity; gecko/traversal remains87e952 with a content pin but no installed identity/ownership. The created cancellation8/depth4 HTML paths must be absent. Only traversal.rs, gecko/traversal.rs, glue.rs and those two tests change. Data.rs remains the font prerequisite. Its message is `No bug - Retain normal descendant restyling after animated font changes. r?#firefox-style-system-reviewers` with the sealed descendant-handoff explanation.

Do not interpose a taint/root-identity native commit or a research commit between the font and cancellation commits: the current exact immediate-predecessor checks intentionally reject that ordering. The font publisher likewise rejects intervening non-artifact changes between e86 and the research predecessor. A different ordering requires a reviewed ancestry-specific successor, not changing these guards. The confirmed reviewer group is already in both messages; cancellation pins the later authoritative mach logc453e09b.

Cancellation evidence includes12 cancellation/depth passes with four improvements/eight preserved/two endings, exact14 font passes, and unchanged root-self7PASS/7knownFAIL/one ending. Startup queue/deeper-chain failures remain unresolved and are neither included as repaired tests nor a reason to relabel these cancellation results. No new build or browser run is required by these publication templates; genuine delivery lint/manifest checks remain mandatory.

If signing fails after installation, the inherited runner preserves a verified pending installation and records SIGNING-FAILURE; it does not automatically roll it back or retry. Stop and inspect that actual state rather than starting the next publisher or rerunning an install into existing output directories. These commits do not rebuild the installed application, and COMMIT-RESULT records accepted=false/accepted_fix_increment=0; acceptance bookkeeping remains separate from signed source publication.

This is a read-only sequence review, not an authority receipt or execution approval. No source/index/canonical/app/Git mutation occurred, and no checkpoint selection changed.
