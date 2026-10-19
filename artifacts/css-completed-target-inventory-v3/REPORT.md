# Completed parser-history generated target inventory

Read-only inventory. **No deletion performed.** Propose one exact completed generated output tree, subject to root's fresh no-use check immediately before deletion:

`/Users/bgrins/code/firefox/artifacts/css-parser-public-history-admission-development-v1/relocated/output`

It contains **300 regular files, 42,392,381 logical bytes (about 40.43 MiB)**, no symlinks. Allocated usage is retained separately in DISK-USAGE.json. The proposed path is generated output outside the source capsule, not the neighboring relocated/capsule, relocated/replay.log, or the entire development directory.

## Evidence and reproducibility

Reauthenticated all 208 source capsule inputs, 110 producer receipt inputs and 437 independent review inputs against externally known FREEZE/MANIFEST hashes; AUTHENTICATION.json records the three exact roots. Both sealed producer and independent fresh replay report PASS, 371 audits and 87 snapshots per native mode. The independent review also passed seven semantic mutations and eight fresh integrity challenges. These findings support deleting redundant products, not deleting the source/evidence that justifies acceptance.

OUTPUT-INVENTORY.json classifies and hashes every proposed file:

| Class | Files | Retention/reconstruction |
|---|---:|---|
| Exact sealed producer receipt | 89 | Each byte-compared with css-parser-public-history-admission-receipts-v1/replay. |
| Generated compiler output | 86 | Lean .olean, Rust .rlib and compiled probe executables; rebuilt from pinned sources/toolchains. |
| Exact source capsule copy | 47 | Each byte-compared with source capsule lean files. |
| Generated native source | 78 | Each reconstructed exactly from pinned crate source, original parser/tokenizer, appended wrapper and the selected literal semantic mutation. No unknown or unmatched file remains. |

Regenerate the complete output with `python3 -I -S artifacts/css-parser-public-history-admission-v1/check.py --run --output NEW_EXTERNAL_DIRECTORY`. The checker requires a new output path, so retaining the old output is unnecessary for rerunning it. Its Lean/Rust toolchains are external pinned prerequisites and must remain. No cargo cache or Firefox objdir is proposed.

## Retain sets

Keep the complete sealed source capsule, sealed producer receipts and sealed independent review at the exact roots in PROPOSED.json. Keep the development directory's relocated/capsule, relocated/replay.log and all siblings of output. Keep this inventory and its file hashes. The sealed producer replay contains one additional driver.log outside the output correspondence; it remains in the retained receipt root. A command's historical output paths may point at the removed directory, but all needed command stdout/stderr, audits, mutation diagnostics, bindings, raw snapshots and final receipts remain in the sealed source/evidence packages.

Other nearby directories are measured only in DEFERRED.json and **not proposed for deletion**. Their earlier development evidence and possible reuse were not individually adjudicated. Do not treat a .olean/.rlib extension count as authority to remove an enclosing directory.

## Active-use check and exclusions

The initial sandbox ps request was denied by the OS. An authorized read-only escalated check at the timestamp in ACTIVE-USE.json succeeded: no matching process arguments for this development root; lsof +D on the exact proposed output returned no open files (exit 1, empty stdout/stderr). This is a point-in-time observation, not a lock or proof that no future invocation could reuse a product. Root must repeat its no-use gate before deletion and coordinate any producer reuse.

No files under css-parser-wrapper-history-proof-v1 or objdir-full.noindex were inspected for cleanup, proposed or changed. No live native/WPT/Git/browser/build operation occurred. This task generated only the small inventory/report artifacts and no compiled targets of its own.
