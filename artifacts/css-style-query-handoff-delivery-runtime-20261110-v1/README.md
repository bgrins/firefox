# Final WPT acceptance for bug 2085413

The exact final 102-line WPT has thirteen callbacks. Against the current local
baseline it records 3 PASS / 10 FAIL; the unchanged two-file query-handoff
candidate records 13 PASS / 0 FAIL. Both harnesses complete OK. The candidate
build exits zero. All three prior passes are preserved. These are manifestations
of the same known bug 2085413, not ten new issues.

Both runs request STYLO_THREADS=4. This configuration exercises the collector
with multiple producers and a deep tree; no trace proves how many workers
actually executed each callback. The final file covers named/unnamed queries,
ordinary controls, depth 256, eight target siblings, pseudo and hidden targets,
nearest-container overrides, registered noninherited custom values, two animated
producers and hidden-then-revealed content. On/off/on samples are checked. The
reveal case can use normal invalidation for its first reveal; later samples
exercise updates in the visible subtree. The fixture has no diagnostic dump,
forced-rematch or frame-wait code.

ROOT-COMPARISON.json independently authenticates every raw test event, exact
roster, native source hashes and identical fixture bytes. Fixture SHA-256:
d8eced0712ae27f9fd50deced397feb7ef39113b94ea7fe6b73bf9aa2654bc51.
Patch SHA-256:
75ab9dc8feec80bae0ac17a4b3cdf141373372283c2cb6721491dd7ea3993d1b.
The preceding broader comparison preserves twelve font tests and verifies the
timeline-query cases too. It is retained in css-style-query-handoff-native-20261110-v1.

The transaction and independent checks restore both native sources, the full
baseline app, three build extras and the original Git HEAD/index; owned process
groups are terminal and absent, temporary WPT removed and both app backups
removed. Receipts bind historical checkpoint04bf4f36c804. The active objdir is
retained. No production file is left modified by this experiment.

run.py accepts a fresh output directory and optional `candidate` argument. It
uses the pinned existing baseline without compilation, or installs and builds
the two candidate files, runs the exact WPT, then restores the baseline. The
runner derives from the prior validated transaction; PROVENANCE.json records
its changes. No Try, push or external submission occurred.
