# Quoted EOF backslash parity repair

The standalone repair preserves escaped pairs of terminal backslashes and removes
only an unmatched final backslash. On the endpoint-fixed branch, this decision
is recorded before constructing reference endpoints; the final pop shares it.
The two exact native/WPT patches are kept separately because the stack version
uses the earlier endpoint repair's state.

Root read the complete terminal grammar and parity proof, source delta and native
extraction/checker, then ran a fresh source replay. Two modules pass 20 exact
audits; standalone, endpoint and combined native configurations pass their
expected semantic projections and compiled mutant controls. Independent source
and final browser-binding reviews are sealed separately. The theorem scope is
conditional terminal-run semantics, not complete Rust/CSS parser verification.
Lean negative files assert false propositions; they do not mutate the definitions
and replay an unchanged theorem suite. Native mutant coverage is separate.

The new WPT goes from four failures/fourteen passes to eighteen passes. The
broader diagnostic fixes the same four cases and retains four escaped-quote
failures. Fifty other outcomes are unchanged, including all 38 endpoint checks.
Build and WPT lint pass. Aggregate WPT exit remains 1 for the separate diagnostic
failures. Build progress-monitor KeyErrors are retained in the successful log.

Both minimal two-file patches apply and reverse exactly at their recorded bases.
Standalone source differs from upstream only by the reviewed late-pop predicate;
its WPT is byte-identical to the paired test. An isolated upstream browser build
has not been run. The proof/evidence commit precedes each native/WPT commit.
