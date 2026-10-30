# Snapshot candidate postrun verifier

Disabled adaptation of the executed masked-controls root verifier, whose actual run was 56092/4312c9/0. The only verifier changes are seven explicit source roles instead of one, nine callbacks instead of seven, four OK page endings instead of two, and the terminal's ending count. `verify.py.diff` is the complete executable delta. The active candidate owner is pinned to `5b28cbbfc0463a3ec72ebbc08e90dadaf540fc4e3c84982d4e1ec53b0331bf11`; its completed original baseline is the frozen nine-case runtime `b38215f9a1967236a18ba4983fe37ae4afe9b4469a779cd1be26c4491d7a3595`.

Preparation reads no candidate runtime, native source, application, index or live process state. Candidate session 33133/launch f91b29 is only a root-reported launch, not a terminal or outcome. Execution remains false until root has the actual terminal and result digest and reviews activation.

The verifier accepts only a successful linked build followed by a complete ordinary PASS/FAIL observation, owner exit 0 and independently verified restoration. Browser exit 1 and a false comparison verdict remain valid measured outcomes, never rewritten as PASS. It replays both exact raw streams using the sealed assessors, joins all paired statuses and expectations through OUTCOMES, and preserves nine callbacks and four endings. It verifies both PHASES snapshots, application metadata, candidate compiled-source and binary hashes, resources and manifest.

All seven sources pass the unchanged restoration loop: exact restored set, base bytes, original inode identity from CANDIDATE-PRE, and a live owned-file claim. This includes AnimationCollection.h, ServoTypes.h and nsAnimationManager.h even though the earlier canonical build did not explicitly pin them. No header is omitted because it is absent from that pin map. The candidate admission already requires their current/HEAD/20ab source-equivalence checks; this verifier additionally requires their candidate build hashes and exact inverse restoration. It does not fabricate historical compiler-consumption proof.

Accepted payloads, context pins, full application and extra-file inventories, root/nested flags, semantic state and process-group absence use the executed predecessor's checks. Backup accounting must match the original preimage and BACKUPS receipt, the owner must already have verified and removed its backup, and the backup path must be absent. This helper never deletes a retained backup.

A compile failure, incomplete stream, infrastructure error, preservation failure or retained backup is unsupported and stops verification. It cannot turn a partial build into a successful trial. Such an outcome requires separately reviewed recovery; do not enable this helper to bypass its successful-build requirements.

The only canonical mutation, when root executes after all checks, is the unchanged byte-owned raw-index-observation replacement with verification and rollback. All other epoch fields, OWNED and ROLE are preserved. Runtime receipts are exclusively created and then frozen. The raw-index update and rollback tail is byte-identical to the executed predecessor.

Saved-only check:

```sh
python3 -I -S -B artifacts/css-contextual-duration-masked-snapshot-root-review-v1/check.py
```

The check covers 20 callback-count/comparison combinations, one exact paired-result reconstruction and 29 negative cases. It also verifies the unchanged source/application/full-state block and raw-index tail. It does not compile, run a browser, invoke a live guard or inspect the active runtime.

After the actual terminal and root activation:

```sh
python3 -I -S -B artifacts/css-contextual-duration-masked-snapshot-root-review-v1/verify.py --session 33133 --terminal ACTUAL_TERMINAL_CHUNK --exit ACTUAL_EXIT --result-sha256 ACTUAL_RESULT_SHA256
```
