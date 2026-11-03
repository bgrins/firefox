# Root font handoff: local cost and correctness

Four fresh headless profiles ran the exact `css-root-font-handoff-cost-probe-v1/probe.js` function against archived broad, selective, selective, then broad candidates. Launch preferences were empty and identical. All 192 samples passed the independent numerical and calibration checks, including 48 warmups and 144 measured samples. Each run used 0, 1000 and 5000 fixed-font leaves.

| Leaves | Broad per-run/per-direction median | Selective per-run/per-direction median |
| --- | --- | --- |
| 0 | 0 ms | 0 ms |
| 1000 | 0.5–1 ms | 0–0.5 ms |
| 5000 | 1.5–2.5 ms | 1–1.5 ms |

SUMMARY.json preserves each run and direction separately, including all measured durations. RAW and REPORT files retain every warmup, result and calibration. Timers were quantized to whole milliseconds; a zero is below observable resolution, not zero cost. The selective candidate was directionally faster in this small local workload. This does not establish a representative browser speedup or prove which native traversal route ran. Existing traversal counters are the next attribution check.

The broad candidate forces descendant recascade after the root-font signal. The selective candidate includes the separate font-unit animation admission prerequisite and forwards a conditional ancestor-font hint. These are cumulative candidate comparisons, not a measurement isolating a single source line or the pristine branch.

BINDINGS.json authenticates both archived applications through their native build snapshots and the existing archive verifier. PRE-ARCHIVES and POST-ARCHIVES match, each covering all 8326 application files. The exact probe SHA-256 is recorded in PROBE.json. Browser configuration and raw connector responses were retained for each run. All four browser sessions were closed, the connector configuration was reset, and 137507796 bytes of owned profile data were removed after process absence and directory identity checks.

Actual preparation: exec7c6e2e/session75878/terminal77408c/exit0. Actual independent assessment, archive verification and cleanup: exec60e8ae/session74216/terminalc3651f/exit0. No native source, Git index, shared application or accepted-fix count changed.
