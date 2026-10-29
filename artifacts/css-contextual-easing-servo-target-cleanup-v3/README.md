Proposes removal of only the completed runtime5 target after root review.
Both full style checks and preservation passed. No future target reuse is
planned. The target contains241,430,528 allocated regular-file bytes across
1,487 entries. Its full identity/mode/mtime/size/hash inventory remains local;
PROPOSAL.json pins it. No target or cache body was copied into this package.

All warning-referenced generated sources are retained outside the target by
completion-v1. The existing5.4MB properties body is reused and only448,400 bytes
of other generated source were copied. The complete warning audit now replays
read-only using those retained sources; it does not read runtime5 target paths.
Raw runtime logs, command/result/terminal receipts, and compressed diagnostic
maps remain preserved. Runtime3/4 cleanup belongs to the separate v2 proposal.

Before removal, root authenticates this seal and runs verify.py. It checks the
sealed completion, all preserved runtime receipts, absence of all five recorded
process groups, the full target inventory/identity, and every warning pairing
against retained source. Any drift requires review. Root then reconfirms no
new owner or future reuse, checks the directory identity immediately before
removal, and removes only the exact target path in PROPOSAL.json. Preserve all
other runtime, closure, completion, generated-evidence and local-audit files.

After removal, rerun completion-v1/audit_warnings.py --check and record target
absence, actual terminal, inventory/proposal/completion hashes, and preserved
receipt hashes in runtime5/TARGET-CLEANUP.json. Agents have not deleted anything.

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-target-cleanup-v3/verify.py
```
