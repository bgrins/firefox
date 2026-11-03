# V129 research checkpoint preparation

This disabled checkpoint follows successful signed V128 research `cb5bb52e3a1645f8eaf5db40cf727c4da36cac8b`, whose sole parent is font-unit native commit `334937d9ef8537e95cb80b29295797bc78f44252`. The exact V128 receipt is `e0256b7f3e9f52b5ac2f6b10cc765921ee9cae890752d5c118b98c4c2fd86bb8`. No additional native fix is admitted.

Cancellation installation `46d940 / 76828 / 54df8c / exit 1` failed after source/test writes when its second new test attempted exclusive creation of the existing `CREATED.json` journal. It was a publication-tooling error, not a new source defect or a pre-write failure. The actual production rollback and independent root audit `d73758 / 89017 / 71f98d / exit 0` restore the source hashes and identities, remove both tests, preserve ownership/role, and verify the full current state. The sealed failure capsule is `1fd13691…`.

`validate_research_rollback` admits the exact signed research receipt and audited post-rollback state. It authenticates the actual failure and audit terminal, reconstructs old epoch `41eaf3b1…` to current epoch `94ca2877…` by changing only `raw_index_observation.current`, and projects the failed install's PRE snapshot to the same actual raw index. It requires unchanged OWNED/ROLE, clean semantic index, restored sources, absent tests/lock, and the unchanged font publication marker. The font receipt `4104034e…` remains separate native provenance. No raw-refresh receipt is invented and no recursive historical replay is introduced.

The V128 transaction from manifest handling through exact selection, private-index staging, blob checks, configured signing, rollback and canonical verification is unchanged except version/message text. The completed-attempt no-retry guard remains. `CAPTURE-DELTA.patch` retains the full live observer and control/source/index/lock checks, replaces the prior native-receipt admission with the actual research/rollback admission, and checks the research commit's sole native parent, artifacts-only difference, and signature. Root owns capture and any later signing; this preparation does neither.

Selection contains completed research and publication evidence, the corrected disabled cancellation publisher, the tree proof, standalone alternative plans/disabled recipe, and roadmap189. Already committed exact blobs are excluded using the immutable V128 commit tree. The nested repository's 25 tracked dependency paths remain excluded with their existing pins. V128 and failed cancellation generated-output directories are selected explicitly as completed files; partial historical manifests are not mislabeled as new complete closures. No live native/WPT path, browser binary, cache, or future outcome is selected. `INVENTORY.json` records the exact classification.

The saved checker authenticates the selection and manifests, immutable parent objects and font blobs, exact unchanged transaction tail, and the actual rollback snapshot. Changed-authority negative controls include dirty semantic snapshots, altered rollback reports, bad terminal outcomes, altered controls, false recovery flags, a non-raw epoch change even with rebound digests, a native receipt substituted for research, pending capture, and the disabled run gate. It performs no live state observation, staging, signing or prior proof/browser replay.

Root capture command, after preserving and reviewing this disabled preparation:

```sh
python3 -I -S -B artifacts/css-research-checkpoint-20261103-v129/capture_current.py > artifacts/css-research-checkpoint-20261103-v129-capture-root.log 2>&1
```

After the actual capture is bound, its closed output/log/terminal and preserved preparation can be included and the package resealed. Root then runs the existing `commit.py --check` before gate-only activation and one normal signed attempt. The message is `No bug - Record cancellation publication recovery and tree settlement research. r?#firefox-style-system-reviewers`. No signing bypass or retry of the failed cancellation owner is authorized by this artifact.
