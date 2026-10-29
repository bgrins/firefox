This is a bounded cleanup proposal, not a deletion receipt. Runtime1's target
is already absent. Runtime2's completed failed baseline target contains
174,052,354 apparent bytes and 177,963,008 allocated file bytes across 1,440
entries. Runtime3 is excluded while its owner runs. No target has been deleted
or modified by this preparation.

Runtime2's generated properties remain an input to the sealed closure-v3
literal audit. Its exact 5,455,782-byte properties.rs is preserved separately
under retained/, with SHA256
bf9ddc30e6a095c3fb16de7e808db704517a60746ab34270b4a52079d2f5e71f.
RETAINED-EVIDENCE.json records both paths and the original auditor/audit hashes.
The retained body can be excluded from a compact research checkpoint while
its hash and provenance are selected; it must remain available locally.

audit_retained.py preserves the sealed auditor's logic. AUDITOR-DELTA.patch
changes only its input locations and replaces its output write with equality
checks against the sealed original audit. It reproduces every original
literal record and count using the retained generated source, creates no
files, and does not depend on the old target. The original committed auditor
is untouched; after cleanup, use this companion replay instead of its old
hardcoded target path.

Before removal, root should authenticate this package and run verify.py. It
checks the observed failure/terminal pins, absence of all four recorded owned
process groups, retained evidence and exact audit replay, target identity,
and every entry's identity/mode/mtime/size/hash. Symlinks, special files, and
hard-linked regular files are rejected. Any drift requires renewed review.
Root must also confirm there is no new owner using runtime2 and no planned
reuse: runtime3's reviewed policy uses its own target. Runtime2 is then a
cleanup opportunity rather than a required compiler cache.

Only artifacts/css-contextual-easing-servo-compile-runtime-2/target is proposed
for removal. Preserve runtime2 command/log/result/terminal evidence, all
sealed capsules, retained/properties.rs, and runtime3. Recheck target identity
immediately before removing it. A later cleanup receipt should bind this
proposal/inventory, actual root execution terminal, preserved evidence hash,
removed target path/identity, and confirmed post-removal absence; rerun the
retained audit afterward. No cleanup execution is authorized by this capsule.

Historical documentation correction: compile-v4 README says command receipts
remain in runtime2, but its actual POLICY.json and execution use runtime3.
This note records the typo without changing the committed capsule.

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-target-cleanup-v1/verify.py
python3 -I -S -B artifacts/css-contextual-easing-servo-target-cleanup-v1/audit_retained.py
```
