# One Rule and matched custom-only payload blocks

Prepared only; no browser/benchmark execution. This is a separate workload from the Rule chain, with a different report schema and generator.

For each selected N (0,32,64,128,256), the generated stylesheet contains a lower-layer opacity:var(--floor), then N matching unlayered blocks containing only --payload:INDEX, then one strongest unlayered opacity rule. The last rule uses var(--floor), revert-rule or revert-layer according to mode, plus a constant --trigger declaration. Payload values differ, so block contents are distinct. Every selector matches the same uniquely identified probe.

All modes must return the alternating opacity 0.25/0.75 after each inline --floor change. Only the Rule mode has one Rule declaration; it stays strongest, allowing the old scan to find its owner near the leaf. The indexed implementation instead enumerates the whole source view on that first trigger, including the unrelated payload entries. The lower-layer winning opacity differs in priority. Ordinary rule collection/custom-property processing still has its own cost in every mode, which the literal and Layer controls retain.

N means payload blocks, not Rule triggers or total matched blocks. Even at N=0, Rule mode has one trigger; literal/Layer modes have none. Do not merge these rows with the earlier chain's N=0 floor. JSON rows use payloadBlocks, version indexed-c-single-trigger-v1 and workload single-trigger-custom-payload.

Defaults remain seven samples, 1024 measured updates/sample and four warmups. Mode/count order rotates, value assertions remain exact, and parsing/initial flush are timed separately. Caps are 256 payload blocks, one-second samples and thirty-second runs. Time guards run between synchronous reads and cannot interrupt a hung call. Workload counters do not prove native index construction or memory usage.

The pure CSS generator was evaluated during preparation and compared against the Python report oracle for all fifteen cases. That is a generator check, not a browser callback or timing run. Use the separate private package css-revert-rule-indexed-single-trigger-wpt-v1 for a pinned paired comparison.
