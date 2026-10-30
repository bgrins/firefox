# Logarithm special values and observer adequacy

This audit reproduces known logarithm failures and identifies a weakness in special-value tests. It is research, not an accepted native fix. The browser tool identified System Firefox 158.0; its executable was not authenticated as this branch or as a release build. Owned temporary elements and tabs were removed. No native source, index, application, canonical library or acceptance record was changed.

Both `CalcNode::resolve_internal` and the `CalcNode::Log` simplifier call the ordinary floating-point logarithm with a base. The captured local source is the accepted pow version. Searchfox's existing `exp-log-compute.html` and its metadata match the local files exactly. Four expected failures already cover base one, and another covers the sign of `log(1, 0.5)`. Those are prior art, not new discoveries. A subject search of all 149 accepted ledger entries found no logarithm repair; this is not an exhaustive external duplicate search.

The current [CSS logarithm rules](https://drafts.csswg.org/css-values-4/#exponent-infinities) reject base one and negative bases, propagate NaN, and prescribe special results for arguments zero, one and positive infinity. The zero and infinity rules are stated without an exception for positive bases below one. The draft does not explicitly settle base zero in that paragraph, although existing WPT expects NaN there. Keep that discrepancy open; browser behavior is not a specification oracle.

| Expression | Observed class | Interpretation |
|---|---|---|
| `log(2, 1)` | positive infinity | Known base-one failure |
| `log(1, 0.5)` | negative zero | Known zero-sign failure |
| `log(0, 0.5)` | positive infinity | Opposes the draft's stated zero-argument rule |
| `log(infinity, 0.5)` | negative infinity | Opposes the draft's stated infinite-argument rule |
| `log(2, 0)` | negative zero | Existing NaN WPT can miss this; base-zero rule needs clarification |
| `log(0.5, 0)` | positive zero | Same unresolved base-zero boundary |

`BROWSER-OBSERVATION.json` contains twelve constant-expression probes. `CONTEXT-OBSERVATION.json` contains four deferred expressions evaluated at font sizes 0, 2 and 0 pixels, including base-one and signed-zero failures. That probe reassigns the declaration at each sample, so it demonstrates contextual evaluation, not independent mutation-invalidation coverage. The source uses the same operation in both folding and resolution; these browser results alone do not prove which native path executed.

`numeric-testcommon.js` tests NaN by comparing both the expression and its negation with NaN after computed-value conversion. Zero and NaN can both become zero there. `SpecialValueObserver.lean` makes that blind spot explicit and proves that adding the reciprocal and its negation distinguishes all five modeled special values. The observer uses opacity: the four samples are the expression, its negation, its reciprocal and the negated reciprocal. The [CSS calculation rules](https://drafts.csswg.org/css-values-4/#calc-ieee) supply the special arithmetic and top-level NaN conversion premises; opacity range clamping is a separate model assumption.

`OBSERVER-OBSERVATION.json` calibrates all five special values in the actual browser, then applies the observer to six logarithm cases. Negative zero is constructed as `(-1 * 0)` rather than assuming a literal `-0` retains its sign. The nine Lean theorem audits passed; three deliberately false controls were rejected. Only `propext` appeared in axiom output. Replay used session 4818, terminal f0329e, exit 0, and removed its temporary compilation directory.

The proof covers only the five-element special-value model. It does not prove floating-point logarithm correctness, CSS parsing or native refinement, distinguish arbitrary finite magnitudes, or add canonical library coverage. Discovery was source/spec/browser driven; Lean establishes the adequacy of the stronger observer afterward.

Next: validate these cases against the authenticated branch, retain ordinary and NaN controls, and check both literal and deferred evaluation. Resolve the base-zero specification question separately. A repair should share exceptional-value dispatch between folding and resolution and carry its own WPT; none is installed or accepted here. Min/max's broader regression run remains ahead of this follow-up.

Replay the bounded proof into a new output directory:

    python3 -I -S -B artifacts/css-log-special-value-audit-v1/replay.py run-2
