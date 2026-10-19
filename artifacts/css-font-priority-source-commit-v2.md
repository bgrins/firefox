# Font priority source companion

Commit the 93 authenticated inputs, INPUTS-v2.json and check.py under
css-font-priority-proof-v2, plus this guide, before the separate six-file
Gecko/WPT repair. The exact 96-path inventory is in
css-font-priority-fix-v1/verification-final-v2.json. The source closure includes
the prior generated C++ sources needed to check the final include-only refresh;
browser profiles, executable binaries and run logs are excluded.

Authenticate check.py separately: SHA-256
`13c91c2617e176ac8ff47e37fdee0bc42461c4c5fc45c236df6ec15de765512d`.
The input manifest SHA-256 is
`aab36f78467284b8b64bd11348262b98717a994447a8d161608c5b6d5018eb45`.
From the repository root, choose a fresh output directory:

```sh
python3 -B artifacts/css-font-priority-proof-v2/check.py \
  --out /private/tmp/font-priority-new-replay
```

The checker authenticates all inputs before local helper imports, then copies
the source closure and rebuilds the native experiments. The pinned Lean/clang
toolchain and SDK are external prerequisites. This is source isolation, not a
hermetic compiler distribution. Historical receipts and live Gecko source are
not needed for replay.

The approved contract includes 32 Lean theorems and 11 semantic witnesses,
the five complete matching consumers, global fallback orchestration and the
declared provider branches. Native comparisons cover 53,628 harness rows:
30,204 consumer-entry rows, 23,412 helper-only rows, four fixed-point/default
provider rows and eight ABI rows. These are not dynamic invocation counts.
Eleven native semantic mutants and their Lean witnesses distinguish the
intended policies; narrowing individual coordinates is an explicitly recorded
no-op control. Independent review adds 10,000 directional selection cases.

The mathematical proof assumes the admitted descriptor and provider domains.
Bounded native agreement does not establish general C++/IEEE refinement,
platform shaping, loading, lifetime, IPC, locking or concurrency correctness.
Instrumented extraction timing checks preserve provider work and checksums;
they do not establish browser performance.

Root and independent full v1 replays passed. The v2 refresh keeps the theorem,
oracle, corpus, driver, mutation and provider inputs unchanged, corrects count
labels, and binds the final header without its unused math.h include. All four
generated translation units and 57 deterministic receipts agree with v1.
Fresh producer and independent v2 replays pass; root reviewed and replayed the
refresh and independent checks. The final production build and WPT pass.

The repair contains five gfx/thebes files and
fractional-font-matching-priority.html only. The exact original, A-only,
B-only and combined matrix shows A's 12 failures become 26 passes independently
of B's separate oblique-threshold repair. Six existing reftests and four parser
subtests pass; three existing expected failures remain unchanged. Final lint
reports zero errors and one ignored-WPT warning.
