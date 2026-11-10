# Bounded animation request-to-installation trace

The instrumented producer-local combined candidate delivered every selected request cohort in the two measured activation intervals to actual style installation before the getter returned. Both WPT callbacks passed. This supplies bounded native evidence for the earlier obligation-conservation model; it does not prove native refinement or termination. Held repair #160 remains held, and no browser repair entry is added.

| Interval | Request events | Selected cohorts / installations | Drain selections by iteration | Getter |
| --- | ---: | ---: | --- | --- |
| Startup activation | 21 | 10 / 10 | 4, 3, 2, 1 | 512px |
| Second callback activation | 22 | 10 / 10 | 4, 3, 2, 1 | 512px |
| Unrelated style mutation | 0 | 0 / 0 | none | 512px |

The later unrelated mutation performs one ordinary style installation, outside the animation-delivery counts. The two activations use four nested animated elements, a literal root font size and multiplier two. They exercise ordinary elements at the animation cascade level only; transition-level and pseudo-element delivery are not tested here.

## Candidate and execution

`SOURCE-ROLES.json` distinguishes the original eight native files, the three-file semantic change, and the eight-file instrumented candidate. The semantic candidate combines the already-tested producer-local handoff with the dependency drain. It preserves the current root-identity and stylesheet fixes. `semantic.patch` contains only that combination; `instrumentation.patch` contains diagnostic additions. `native.patch` is their combined difference from the recorded base revision.

`run.py runtime1` ran a native build and one headless WPT with `STYLO_THREADS=1`, `MOZ_ROOT_FONT_DRAIN_TRACE=1`, and dump output enabled. Both commands exited zero. The raw harness result is two PASS and one OK. `runtime1/BUILT.json` pins the actual candidate source and binary hashes; command receipts, full build output and raw WPT output are retained. A nonfatal Mach progress-reporting `KeyError: 'export'` appears in the successful build log. No new A/B comparison or broad-handoff timeout was run.

`font-dependency-ledger.html` is a diagnostic reduction of the earlier settlement WPT, with three dump-delimited observation intervals. `FIXTURE.json` records the source and diagnostic hashes. The temporary live WPT was removed after execution.

## What is checked

`analyze.py` reads the saved raw JSONL. For each selected cohort it checks:

1. Earlier request events with the same compositor, target, full pseudo request and cascade level.
2. Pseudo resolution in `RestyleManager::PostRestyleEvent`, including a non-null normalized node and the matching animation/transition hint.
3. Actual hint insertion in `GeckoElement::note_explicit_hints`, not just the attempt to post it.
4. The same full key at composition and queue-removal intent.
5. A matching animation-only restyle and an installation event after `data.set_styles(new_styles)` in style matching, in the same document traversal call and thread.

The checker also requires queue-count agreement at the observed pre-traversal boundaries, one compositor/document/style set/thread per interval, complete document-call nesting, no outstanding observed request cohort at interval end, and four nonempty activation drain iterations. It preserves newer requests separately from cohorts already selected. The saved `ANALYSIS.json` identifies every joined raw record using zero-based JSONL indices.

Twelve deliberate trace mutations are rejected: missing hint insertion, missing installation, wrong cascade level, wrong pseudo argument, wrong normalized node, ordinary traversal substituted for animation delivery, missing request cohort, a newer undelivered request, trace capping, interleaved records, wrong document call and a different installer thread. `OPTIMIZATION-CONTROLS.json` separately records rejection of optimized Python execution in each assertion-based entry point.

## Limits

- This is a replay checker over observed events, not a proof that the logger captured all native operations. It cannot establish absence of unlogged work or correct animation values from the ledger alone; the WPT checks the getter value.
- JS markers lack a native PID or document token. Content attribution is inferred from the unique process producing selections within each activation interval, checked consistently across both callbacks, then reused for the mutation interval. The matching document/compositor identities strengthen that inference but do not remove the instrumentation boundary.
- The full log contains 146 malformed **tagged** records outside the marked intervals, caused by interleaved diagnostic writes. Untagged fragments outside those intervals are not classified. Every process-output record inside the intervals is parsed strictly; no malformed record or cap is accepted there. No claim is made about whole-run conservation. WPT harness events arrive on a separate channel and can interleave with buffered process output; their placement is not used as a native causal clock.
- The finite fixture retains its nodes and animations across each synchronous interval. Pointer identity is used only within those intervals. No general allocation/lifetime or ABA invariant is proved.
- Request-event indices define observed cohorts; they are not native generation counters. Checking coalesced delivery does not prove that all possible native requests may be coalesced safely. Only non-throttled request types occur in these intervals.
- `select-remove` records intent before queue removal. Queue-count checks and subsequent delivery support this execution, but missing-EffectSet retirement and other early exits remain outside the measured path.
- The installation hook observes primary style after the actual style swap. It does not prove every required effect was composed correctly, nor does it cover all pseudo styles.
- Four descending selection counts on depth four are evidence for this fixture, not a general decreasing measure. Reentry, arbitrary dependency graphs, generation freshness, failed-post retirement and scheduler convergence remain open native correspondence obligations.

## Restoration and replay

The runner restored all eight sources, the full application bundle and three external application/test files. It verified the original HEAD and index, removed the temporary WPT, terminated its owned process groups, and removed its 1,008,637,464-byte backup. The independent `ROOT-RESTORATION.json` audit repeated those checks and verified the preceding first-order IR commit signature. The current manual browser remains the committed scope-cache build. This is application restoration, not rollback of every intermediate objdir product; restored source timestamps require subsequent builds to reconsider the affected inputs.

Replay the trace without a browser or build:

```sh
python3 -I artifacts/css-animation-obligation-native-20261110-v1/analyze.py
```

Replay exact source preparation without editing the live source tree:

```sh
python3 -I artifacts/css-animation-obligation-native-20261110-v1/prepare.py
```

The latter reconstructs the eight files from pinned Git revision `037d606ccd2711b2e84c286991005e2eb96c4f0f`, applies the two patches without fuzz/offset, checks all 24 role hashes and removes its temporary directory. `--materialize` additionally creates owned base/semantic/candidate copies for a new native experiment. `prepare-original.py` preserves the original derivation recipe; `PREPARATION.json` and `prepare.log` describe that historical preparation. The final replay does not depend on those archival source directories. Full copies and Python cache files were removed after successful reconstruction; `CLEANUP.json` records the reclaimed bytes.

`verify_restoration.py` checks the captured pre-commit state and is intentionally tied to the original HEAD/index. Its saved successful receipt remains the record after this research is committed. A future native run needs a fresh output directory and review of the baseline/application pins; do not overwrite `runtime1`.

Next: establish a structural decreasing measure for the producer-local dependency work and map it to the native transitions, including new requests produced after an earlier cohort is installed. The current trace closes a delivery-observation gap; it does not justify lifting the hold on #160.
