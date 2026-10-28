# Standalone zoom source transition

Reviewed, unexecuted transition from the nine-file admission-plus-zoom prototype to committed HEAD, followed by the seven-file zoom-only candidate. Frozen HEAD is `d6243f35307b62a4a4f6067367d78c948d3f468c`; initial epoch is `41d1feefbef5c50d07e7a873773a3565517a1f1e4b3dcf0d338cd84c4c0daf16`. The disabled v1 recovery package remains immutable. All nine original/prototype bodies are preserved there and authenticated here; actual committed source bytes were rechecked at the new HEAD.

Root executes from the checkout with normal local build permission:

```sh
python3 -I -S -B artifacts/css-registered-zoom-standalone-transition-v3/install.py original MANIFEST_SHA 41d1feefbef5c50d07e7a873773a3565517a1f1e4b3dcf0d338cd84c4c0daf16
python3 -I -S -B artifacts/css-registered-number-native-runtime-v1/build.py zoom-standalone-original-build-1
```

After the original build and baseline browser run have completed, root supplies the exact current successful original-build epoch digest:

```sh
python3 -I -S -B artifacts/css-registered-zoom-standalone-transition-v3/install.py candidate MANIFEST_SHA ORIGINAL_BUILT_EPOCH_SHA
python3 -I -S -B artifacts/css-registered-number-native-runtime-v1/build.py zoom-standalone-candidate-build-1
```

The candidate invocation requires the saved original build EPOCH to equal the supplied current epoch, successful cleanup/preservation receipt, exact role/variant/build label, and exact source-transition lineage. Browser validation is owned separately by root; this installer does not claim WPT acceptance. Each install leaves compiled=false, accepted=false; only the existing build helper publishes compiled=true after success. Role variant is `zoom-standalone-v1`, paired HEAD as above. Output directories are `zoom-standalone-original-2` and `zoom-standalone-candidate-1` under the existing native runtime; they must be absent.

Native dirty paths become exactly zero and then exactly seven. The two admission files stay at committed originals in the candidate. The 99 installed source identities, 57 OWNED entries, 50 parked prototypes, 140 recovery entries and 74 untracked project files are separate preserved inventories. Both source and restoration bodies are authenticated once into immutable buffers. Immediately before writing, full epoch preservation, control/source bytes and identities, immutable references and process quiescence are checked. Source writes reuse the reviewed inode-preserving partial-write-aware helper. Runtime controls use atomic replacement, with signal masking until the new control identity is recorded. A transition lock prevents another cooperating source transition. Rollback uses captured buffers and checked ownership.

Quiescence requires every recorded native-runtime command to have a terminal result, the current successful build's owned groups to be absent, the three pinned browser groups to be absent with terminal cleanup, and a calibrated process census to show no matching checkout objdir/browser or mach build/test activity. This is a fail-closed point-in-time check; root must continue to serialize builds and browser runs with transitions. It is not a global OS lock against unrelated launches.

Validation: seven positive and 21 negative controls passed; exact seven-file patch forward/reverse/reapply at zero fuzz preserved both admission originals; scratch was removed. Controls cover stale HEAD/epoch, source and ownership drift, changed control/source identity or bytes, symlinks, changed package, active groups, unfinished commands and bad/busy process census. Actual saved terminal schemas/references and 50/140/74 inventories were checked read-only. Independent bounded review cleared the two earlier safeguards and schema correction. No installer main, browser, build, native/WPT edit, index, HEAD, ledger or epoch mutation was executed by the preparer. This is not a claim of native correctness or accepted bugfix.

## V2 failed execution and narrow correction

V2 wrote original sources but rejected a changed raw-index hash. Its rollback restored all nine source bodies and ROLE/OWNED controls; strict old raw-index verification then failed. Original-1 partial records and driver remain intact. Independent full recovery verification authenticated restored semantics, all pin maps/identities and recovery inventories. Root refreshed only raw_index_observation.current to epoch41d1feef. Cause is unknown; metadata refresh is only a possibility. No pre-failure ls-files-v bytes were saved by v2, so none are claimed.

V3 uses fresh original-2 output. After source edits it still requires exact semantic HEAD/entries/cached diff, nested index and root/nested flags, while allowing expected working diff and raw-index observation to change. FLAGS.json and INDEX-OBSERVATION.json preserve the comparison. Rollback requires full original semantic/source preservation before refreshing only the raw-index observation. Neither path writes Git index bytes. Initial epoch must still equal the exact recovered epoch; there is no general preflight waiver.

Seven positive/21 negative controls and exact patch transport replayed (bcb8c2/0). The actual semantic assertion AST accepted expected source-diff change and rejected HEAD, entries and cached-diff corruption (839cf2/0). Independent bounded review cleared0015c4/0 and96e87d/0. No installer main/native mutation was executed by the preparer.
