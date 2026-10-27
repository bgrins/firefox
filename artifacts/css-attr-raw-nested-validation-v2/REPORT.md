# Raw nested attribute repair acceptance

The fresh paired run repairs all 17 target failures: 56 PASS + 17 FAIL becomes 73 PASS. All 329 regression assertions and six reftests pass unchanged. Original and candidate use the same revised fixtures, including three explicit historical oracle corrections and seven EOF controls. The earlier failed 66-target comparison is retained.

Both native builds and the exact installed WPT lint pass. Independent review authenticates source, binary, metadata, lifecycle and cleanup evidence. The earlier20 native tests remain applicable to identical source and GTest libraries; current normal browser binaries are separately tested by WPT.

The standalone patch contains cascade.rs and two WPTs, and requires signed fix137. It keeps bare/raw attribute reads opaque during dependency traversal. Tentative priority P3: CSS correctness. Source/spec audit and browser reproduction established the bug; the Lean guard model supports normalized semantics but does not prove Rust refinement or EOF parsing. No canonical Lean coverage is added. The minimal head patch has transport/syntax checks; browser execution used the current prototype-bearing branch.
