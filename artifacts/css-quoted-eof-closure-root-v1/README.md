# Escaped terminal quote recovery

The correction recognizes a matching final quote as a closer only when the
preceding maximal backslash run is even. An escaped quote remains string content,
and recovery appends the missing closer. Opening-only strings retain their guard.
No parity or endpoint behavior is included in the standalone predicate change.

Root read the complete terminal grammar/closure proof, checker, source delta and
native extraction. Fresh replay passes two modules, 19 exact audits and native
original/candidate/mutant runs in standalone, endpoint and combined configurations.
Two independent reviews cover the source/proof and final composition/WPT pair.
The exact composed source is unchanged by formatting. Lean scope is conditional
terminal-run semantics with explicitly admitted tokenizer/native correspondence.
Negative Lean assertions are not whole-definition mutation tests.

The independent WPT changes four failures/fourteen passes to eighteen passes.
The broader diagnostic now passes all 22 cases; all 18 parity and 38 endpoint
checks still pass. Across 111 keyed outcomes only the expected eight status
records change (four cases duplicated in the diagnostic). Sixty-nine other
outcomes are unchanged; three known expected syntax failures remain. WPT exits
zero, with no unexpected result. Build and WPT lint pass. Full raw logs retain
the build progress-monitor KeyErrors despite successful compilation/linking.

Two-file stack and upstream-based patches apply and reverse at recorded bases.
The upstream version differs only by the reviewed predicate and identical WPT;
its separate proof companion precedes the native commit. Browser validation is
shared-tree only, not an isolated upstream build. Tests are compared by outcome
key, because file execution order differs between the paired runs.
