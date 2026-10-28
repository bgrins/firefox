# Reversible linear second-position guard validation

Reviewed capsule for root execution at signed HEAD b1cae69e67ccfb707b4d9010d34386009e01d9c2 and canonical epoch e804d29fdeb683e75639ec4b1c16359e799e9a14e8c5826c23b07e5b28bc76fc. The only candidate source is easing.rs from the sealed formatting-corrected guard proposal v2. The configured check belongs to proposal v1; this experiment must make a fresh linked build of v2. No native acceptance or new fix number is allocated here.

The owner retains one exclusive restoration scope across these separate operations:

1. Build original sources with `mach build binaries -j2`, saving the real compiler result and a phase-local epoch with actual rebuilt binary hashes.
2. Run the 40 existing regression tests and two feature calibrations as `original-baseline-1`, requiring all 42 identities and three OK endings.
3. Run only the six-target page as `original-crash-1`. The WPT adapter must positively certify the exact target crash/process evidence and preserve partial events. A timeout, infrastructure error, missing event or arbitrary crash cannot pass. Generic testharness completeness is intentionally not required for this one mode.
4. Install only the buffered, authenticated easing candidate; build binaries again. Run all 48 cases as `candidate-1`, requiring six targets PASS, both calibrations PASS and exact original regression signatures.
5. Once all owned processes are absent, restore the easing source and original application/output bytes, verify full preserved state, and remove only the owned large backups after complete success. Failures retain backup evidence; ambiguous ownership fails closed.

The callable runner uses the existing six-argument interface after the Python flags: capsule SHA, phase name, absolute saved build epoch, epoch SHA, absolute output directory. Outputs are fixed under artifacts/css-linear-second-position-reversible-pair-runtime-2: original-build, original-baseline-wpt, original-crash-wpt, candidate-build and candidate-wpt. Each assessment must report execution_preserved and phase_gate_passed; complete is additionally required for both noncrash modes. Build epochs carry reversible_linear_guard_phase with original/candidate source role and exact owner/build paths. CURRENT, ROLE and OWNED are never published or changed by this experiment.

The existing full clean-index guard remains in use. Accepted fixes 141 and 142 are explicitly joined to all nine body hashes, installed identities and committed HEAD blobs, then checked again through owned claims throughout the run. The held provider stays unchanged. The local observation adds only the easing identity if absent; the existing easing base pin must match. Raw root-index drift is recorded separately with unknown cause and never silently reconciled into canonical CURRENT.

Backup scope reuses the successful counter owner: all regular Nightly.app files, directory and symlink topology/modes (without following symlinks), external dist/bin/gtest/XUL, resolved build/application.ini and wptrunner.local.ini. External symlink referents and general compiler caches are not claimed restored. All four actual rebuilt binary paths are distinct regular files with nlink one and no canonical inode contract; installed release binaries stay immutable. Current sizing is 1,008,605,496 bytes, requiring 38,589,569,336 bytes free before backup to retain the existing 35 GiB build-start floor. The observed free space was 37,735,108,608 bytes, leaving an 854,460,728-byte shortfall. No floor is weakened. Root is separately assessing owned cleanup candidates.

Build lifecycle, cancellation, 45-second cooperative WPT-wrapper cleanup, separate child-group verification and bundle restoration reuse the reviewed predecessor. Forced cleanup retains a surviving temporary directory whose original creation identity cannot be proved. This permits safe restoration after process absence, but does not make the test phase pass. Scratch-only bundle and cleanup controls passed; no real process was signaled and no main function or live guard ran during preparation.

The root command after confirming an exclusive window and adequate free space is:

```
python3 -I -S -B artifacts/css-linear-second-position-reversible-pair-v2/run.py e804d29fdeb683e75639ec4b1c16359e799e9a14e8c5826c23b07e5b28bc76fc OWNER_MANIFEST_SHA
```

This successor is enabled and pins the reviewed runner v2 plus actual root recovery/cleanup receipts. The live free-space guard must still pass; the preparation-time shortfall is not waived. The original and candidate tests are separate subprocess phases within one owner so every exit still reaches the same restoration path.

The first owner attempt (root session 40597, terminal 972325, exit 1) stopped at the post-backup free-space assertion before creating a transition lock or starting any build, source write or browser. Root completed exact unused-backup recovery (session 59938, terminal b02b9d, exit 0), preserving source, application and controls. Its sealed receipt is bound in POLICY. This successor uses a fresh runtime directory; its owner code, source roles, binary restoration, three phase gates and 35 GiB floor are unchanged. Additional cleanup does not replace the immediate live preflight disk checks.

Root cleanup 2 completed (session 48562, terminal 48aec5, exit 0), preserving source, indexes and controls. The recorded free space afterward was 39,675,842,560 bytes. This is historical prelaunch evidence; the owner still recomputes backup size and checks the unchanged live disk floors.
