# Common-only45 owner V2: correct expected modified paths

V1 actual16539/335776/e6dc66/1 completed its build with exit0, then failed in candidate_verify before browser execution. Saved FAILURE-TRACEBACK identifies the epoch verifier assertion comparing actual native modified paths with the expected set. V1 unconditionally added all three owned roles, although common-only cascade equals HEAD. The failed owner/result/backup and original evidence remain preserved; no browser preservation result exists.

V2 changes only the candidate expected-path calculation plus operation/output labels and saved checks. The new set is (previous modified paths minus owned role paths) union (owned roles whose candidate SHA differs from authenticated HEAD SHA). This retains unrelated existing edits, excludes unchanged owned files, removes an owned prior edit when a candidate exactly restores HEAD, and retains a held candidate that differs from HEAD even if its owned preimage matches it. The actual common state expects provider and value only; cascade remains owned/restored and byte/inode checked as the third role.

HEAD pins are policy.committed_source_preimages, authenticated by the unchanged baseline.guard via actual git show for each owned path at policy.head, alongside current HEAD/semantic-index checks. Candidate bytes remain hashed directly on every candidate_verify. The full unchanged-path diff guard, strict epoch modified-set equality, index flags, all three install/restore loops, source identities and app/backup restoration are retained. This is not removal of the epoch guard or a filter hiding unexpected changes.

Saved893b9a/0 tests six concrete path classifications, rejects a missing HEAD pin, authenticates all saved references/source pairs and computes the actual common two-path result; the old unconditional union produces the wrong set. No native/Git/index/app/control/build/browser operation occurred. Saved terminal/trace/build records were read only after root authorized terminal evidence.

Actual current admission now authenticates frozen failed runtimef613e67032dd9d927a0c663d94d9fd342f2ae849906401343efa0a31bda4382f and independent reviewer45029/1ed16e/7e2147/0, report22b1a64a4ac5feb454d6f975a34695e236c207445ad358b0827b01ddbcf36fc5. ROOT-TERMINAL preserves owner16539/335776/e6dc66/1, build0 and no browser; no fictional lifecycle success is introduced. Owner retained-backup evidence remains unchanged; separate ROOT-BACKUP-CLEANUP authenticates verified removal of1,008,605,176B. Raw-only refresh binds epochf2d782b8756404173b9c6de1259319acfd591e92d475185534effa92a12d7817, app entry280012711/target280022110 with unchanged bytes/BuildID/20ab revision and all three original source identities. Historical original45 and the immediate preceding narrow restoration are checked separately. Both gates remain false. Exact suite/source proposal is unchanged; no baseline is replaced or rerun.

The future common-only reviewer still requires all45 callback and4 ending full signatures equal original, including the original15 FAILs; owner success alone does not establish neutrality. Actual compiler warnings must be retained/reviewed without suppression. No outcome is predicted for runtime2.

Saved source-only preparation check:

```
python3 -I -S -B artifacts/css-registered-color-image-common-only-candidate-v2/check.py --source-check
```

Bound saved check3e2963/0 authenticates362refs, six path classifications/missingHEAD negative,18binding and3terminal negatives, original30PASS15FAIL4OK replay and all45FAIL retention. Original preparation deltas/null policy remain in the package. Final deltas compare with preserved failed V1. No current live reads occurred. Full saved preflight uses candidate.py --check MANIFEST_SHA; only root activates/reseals and runs candidate.py --run ACTIVE_MANIFEST_SHA.
