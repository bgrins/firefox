# Standalone float runtime results review

**ACCEPT the bounded standalone results and historical restoration evidence.** This is an independent evidence review, not a native acceptance decision or a general performance guarantee.

## Correctness and attribution

The raw WPT records contain exactly twelve named subtests and two OK harness ends per phase: baseline eight PASS/four FAIL; float-only twelve PASS/zero FAIL. The same four direct/inline, root/leaf hidden queries improve, with no regression among the eight visible controls. Baseline failures are the exact change-stage first-query width 50 rather than 25 messages. Assertions after a baseline failure are not credited as passing. Candidate PASS covers all assertions in each case.

Both phases normalize the 24 selected sources to saved HEAD. Candidate changes only the float sweep in nsBlockFrame.cpp. The accepted block, column, and Grid overlays are absent in both phases, so this run checks the final twelve-test candidate independently of those overlays. It does not add a nested-block repair claim or prove native pushed-bit/continuation behavior. The earlier 95-case campaign remains separate evidence with a different baseline.

For each phase, independent checks joined all 29 native source hashes, 12 WPT resource/metadata keys, both binaries, and 38 captured nonmissing source/resource files. The cost run's 37 source/binary/capsule pins match the preceding WPT phase. Enabled inputs, readiness seal, final v2 fixtures, exact raw names/order, first-failure messages, and stored receipt hashes authenticate successfully. Build receipts report exit zero in both phases.

## Cost observations

Each phase contains 60 measured rows, 148 exact progress receipts, and 1,968,000 measured geometry reads after one warmup round. I independently recomputed every calibration rectangle, recovery classification, clean-batch checksum, and reported timing distribution from raw receipts; this recount does not invoke the fixture's validator. Both runs report terminal owned-process cleanup, no live group, removed profile, and no cleanup errors.

Baseline has 480 incorrect recovery observations: 80 in each of the six hidden groups, evenly split between first and immediate-repeat queries. Candidate has zero mismatches. All visible recovery queries and clean-query controls pass in both phases. The baseline's stale recovery timing is not comparable as equivalent work.

[The paired table](TIMINGS.md) and PAIRED-TIMINGS.json retain medians and full per-round distributions. Timings are quantized to whole milliseconds. Every repeat sample and every visible first-query sample is zero in both phases, leaving that cost unresolved. At 128 floats, candidate hidden first-query sums have direct median 2 ms and inline median 3 ms per 16 transitions; those are costs of obtaining correct geometry where baseline fails.

Visible preparation medians remain 0/1/2 ms for 1/32/128 floats in both shapes. Twenty of 24 clean hot median pairs remain 2 ms per 16,384 reads; two rise 2→3 ms and two fall 3→2 ms. Ranges overlap, with occasional larger samples. This gives no consistent size-growing clean-query signal in this bounded run, but the fixed phase order, five rounds, timer resolution, scheduling, and combined JS/DOM costs prevent a general performance or regression guarantee. Separate ReflowDirtyLines invocations may still repeat the float sweep; no native invocation counter was observed.

## Restoration

Authenticated the final runtime FILES.json SHA256 `30d2f2372b527289e381b3c5759b558b7e2d53e8a24925a6e9a6b654e38e213c`, all 227 payloads, and its closed file roster. Controller state is terminal/restored, with restoration build exit zero, no failure, and no recovery errors. BEFORE equals FINAL equals the prepared original snapshot, preserving the 29 source guards, HEAD, full native diff, and frozen index epoch.

The sealed ROOT-FINAL-CHECK.json authenticates root's immediate live check: the 925 staged research entries, nine preserved existing tests, absent owned temporary files, stable resources, and restored source epoch. Its INPUTS/STATE/FINAL hashes independently match the sealed files. This review makes a historical claim only; later MathML work may change live state.

The restoration log retains Mach resource-monitor `KeyError: 'export'`, alongside `Your build was successful!`, exit zero, and passing restoration checks. That logging issue is not silently erased or reported as a native compilation failure.

The experiment contains 24 raw subtest observations, four OK harness ends, 120 measured cost rows, 296 acknowledged progress events, and 3,936,000 measured geometry reads. The four WPT failures improve with no passing case regressing. All final analysis artifacts retain `native_acceptance: false`; the parent owns any subsequent native acceptance decision.
