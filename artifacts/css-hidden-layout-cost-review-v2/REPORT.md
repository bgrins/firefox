# Independent cost-v2 source review

## Verdict

GO for the bounded local diagnostic, with the producer's final seal authenticated and subject to the parent driver's cleanup gates. This is source and synthetic validation, not an executed browser-cost or cleanup result.

## Concrete correction

The draft process-list parser silently discarded malformed nonblank rows. A wholly unparsed listing could therefore appear to prove an empty process group. The producer corrected this before sealing: empty listings and malformed/nonnumeric/invalid identities fail closed before group selection. Independent mocked challenges reject those inputs and refuse signals after UID, session, or current-group mismatches and failed inspection.

## Fixture and work accounting

Read the complete HTML, JavaScript, configuration, validator, runner and cleanup helper. There are12 configurations, two discarded warmup rounds and seven measured rounds:84 measured batches. Sixteen mutations per batch, sampled leaf counts1/4/4, and16 no-mutation passes yield13,440 recorded leaf reads. The validator reconstructs exact ordered identities, full visible and initial rectangles, and mutation checksum. It rejects missing queries and bad calibration while retaining target geometry mismatches as data.

The buckets distinguish first leaf, same-leaf repeat, other sampled leaves, a second sampled pass and no-mutation passes. These are observable query timings, not instrumentation of internal layout work. Size1 has no distinct-leaf reads. Each timer includes JavaScript/DOM access and array construction; short samples may quantize to zero. Construction includes a visible peer, and establishment includes calibration. One fixed-order process per variant cannot establish broad absence of regression or causal internal cost. Actual geometry differences must accompany any timing interpretation.

## Process ownership and failure handling

The runner uses a fresh local profile and new POSIX session, records spawn identity, then captures PID/PGID/UID/state/birth and independently queries session/current PGID. Cleanup first terminates/waits for its Popen leader. Group signals require verified owner/session/group membership and a surviving previously recorded identity. Departed groups receive no signal; EPERM and unverified identity remain failures. Bounded waits and final inspection produce explicit terminal/noLiveGroup receipts. Zombies are excluded from live members; the leader must still be reaped.

This is a sampled operating-system ownership check, not an atomic process-lifetime proof. It covers the original process group/session only; descendants escaping it are not proven absent. Permission or inspection failures can prevent cleanup; the parent must then stop remaining phases and restore native sources/build. Profile removal alone never proves process termination. The receipt must require terminal, noLiveGroup, empty cleanup errors, profile removal, and stable binary/fixture/native pins. Calibration or timeout failure may permit later WPT phases only when all cleanup and integrity checks pass.

## Independent checks

Replayed producer synthetic tests without launching browser processes or sending signals. Nine additional mock challenges cover empty/malformed/nonnumeric/negative listings, a valid unrelated group, three ownership mismatches, and inspection denial. Receipts are retained. These checks validate handling of supplied OS observations; they do not substitute for the forthcoming actual process receipts. The producer's read-only host ps-field check is separate from these mocks.

Full hidden-layout correctness, original-key source independence and performance remain runtime questions. No native code, Git state, browser, or build was changed by this review.
