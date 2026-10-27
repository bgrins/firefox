# Counter first candidate capture review

PASS for this completed phase; the four-phase comparison is still running. The browser command exited 0, all 24 new counter cases and 64 quote cases passed, all eight existing regression ends passed, and both harness ends were OK. The first candidate build exited 0 with its owned build and wake groups absent.

I read the current policy, native patch, unchanged WPT, source/spec mapping, model review, driver source review and archive checker. The checker replays raw event parsing and policy against exact source/binary/resource pins and verifies phase process cleanup. Its actual execution exited 0 (tool chunk 89639f). This is an independent inspection using the existing reviewed checker, not a separate browser run or checker implementation.

The native patch marks the shared counter name dirty on insertions into a list whose containment scope has children. It preserves the previous childless branch, existing dirty propagation, and parent-before-child recalculation. The 24 cases cover reset/set/increment, counter/counters, direct/nested uses, and with/without a trailing use; immediate mutation is measured before fresh construction. The formal model remains conditional on valid recipes and native delivery correspondence, not a C++ refinement proof.

This phase does not establish final candidate restoration, repeated original/candidate agreement, overall driver exit, or acceptance. The former tool session handle is unavailable; any later driver RESULT plus absence observation must be described distinctly from an observed outer OS exit code.
