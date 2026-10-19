# Root replay: optimized byte dispatch

The v2 capsule passes a fresh relocated replay. All 28 live source/configuration pins and the complete cssparser Rust source inventory still match; all 22 calls and 5,632 byte decisions are covered. The independent source audit and delta review accept this conditional component.

Six general theorem audits and two concrete counterexample audits pass. Both semantic table mutants fail, and the reader rejects exclusive ranges and a second named binding. V1 remains retained with its admitted two-binding counterexample. V2 also corrects UTF-8 byte offsets. Neither finding is a current browser bug.

The Rust macro/compiler correspondence is an explicit source-reviewed boundary. Complete tokenizer progress, UTF-8 return boundaries, numeric/string/URL providers, arithmetic and suffix-restart semantics remain open. The next component is complete name/escape return-boundary refinement under the real caller's admission conditions.
