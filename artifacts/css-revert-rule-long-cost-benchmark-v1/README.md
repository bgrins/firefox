# Rule rollback timing with longer batches

Prepared without execution. Open `benchmark.html` as a standalone page, or use the private wrapper in `css-revert-rule-indexed-long-cost-wpt-v1`.

This new version changes the earlier fixture only in four places recorded by `PROVENANCE.json`: default rule counts become 0,32,64,128,256; measured updates default/cap becomes 1024; input validation permits that cap; report version becomes `cold-c-chain-long-v1`. The old fixture is unchanged.

Seven samples, four warmups, literal/Rule/Layer controls, a common zero-rule floor, rotating mode/count order, exact alternating opacity checks, setup separation and one-second sample/thirty-second run guards remain. Those guards execute between synchronous reads; they cannot interrupt a hung call. No timings were measured during preparation.

The private comparison fixes 1024 updates/sample for every role. That is 105 samples and 107520 measured updates per repetition. It aims to make baseline batches roughly milliseconds rather than fractions of a millisecond; actual durations remain unmeasured. Larger batches reduce relative quantization error but do not remove CPU/load/GC effects or produce a statistical acceptance threshold. Every timed iteration retains the same property write, computed read, array store and deadline check.

JSON counters remain workload counters, not native lookup counts. No performance or release-exposure claim follows from this prepared page. The proposed single-Rule/unrelated-source workload is documented separately and is not implemented or mixed into these timings.
