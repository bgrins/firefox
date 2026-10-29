# Full Servo check with matching atom dependencies

This capsule selects sealed closure-v4 after runtime3 failed on five missing
mime imports and two atom API mismatches. No native Rust source changed.
DEPENDENCY-API-PROVENANCE.json explains the missing original manifest entry and
upstream Atom::as_str upgrade; the dependency graph now matches that API.
Full compilation remains pending, with no candidate result claimed.

run.py and its tests are byte-identical to reviewed compile-v4. POLICY-DELTA.patch
changes only closure/seal and the initially absent runtime4. The old v4 README
incorrectly named runtime2 for command receipts; this successor records all
commands, versions, logs, exits, and preservation receipts under runtime4.
Previous targets and capsules are not altered or reused by this runner.

Root alone executes after review. Full baseline cargo check uses --locked
--offline -p style --lib --no-default-features --features servo --jobs 1.
Candidate runs only after baseline success. Both use one owned runtime4 target,
no debug/incremental output, and no RUSTC_BOOTSTRAP or lint caps. Limits remain
900 seconds per compile, at least 24 GiB free, and at most 1.5 GiB target bytes,
sampled every 0.5 seconds. Owned groups receive TERM/KILL on limits or signals;
waiting and absence checks remain strict. Inputs are checked before/after and
on final cleanup; preservation failure prevents success. Files that disappear
are tolerated only in live resource samples, with strict initial/final samples.

This checks the captured local configuration, including the shared held
custom_properties.rs at SHA256 2675b33b30ac43db5b758d5a80f42fa4530856c32d5a0923882a15f8a8bc5774.
Seven contextual-easing source differences remain exact. No native acceptance,
clean-upstream claim, or runtime behavior is established by this check.

Authenticate without compiling:

python3 -I -S -B artifacts/css-contextual-easing-servo-compile-v5/run.py --check <FILES-sha256>

After root review, substitute --run. Outputs and retained target go to
artifacts/css-contextual-easing-servo-compile-runtime-4; result is RESULT.json.
