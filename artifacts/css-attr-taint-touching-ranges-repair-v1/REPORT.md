# Proposed half-open attr-taint intersection repair

## Evidence and scope

Root's exact five-case browser diagnostic reports one failure (touching untainted URL and tainted resolution), four controls PASS and harness OK. I independently read the raw events: the failure is the final computed-image assertion, so its typed-resolution, literal grammar and computed-value prerequisites have completed successfully. The raw receipt retains stable source/binary pins. No browser/build is run by this package. The prior source-only audit remains immutable.

The proposed one-expression native change computes whether the intersection of two byte ranges is nonempty:

`r.start.max(range.start) < r.end.min(range.end)`

This preserves overlap and containment in either direction, rejects either kind of endpoint contact, and rejects empty intervals even if they lie inside the other interval. It uses only comparisons, with no added arithmetic or UTF-8 slicing. For valid `[start,end)` intervals it is equivalent to existence of a byte index in both intervals. It preserves the existing any-over-all-taint-ranges semantics.

## Why not just strict pairwise comparisons

For nonempty ranges, `r.start < range.end && r.end > range.start` is equivalent. But an empty taint range strictly inside a URL range would pass that expression. The API explicitly allows `start == end`; selecting max/min makes the helper consistent for that entire documented domain without silently adding a nonempty premise. Empty spans represent no produced bytes; whole-substitution taint semantics still travel through the existing boolean and producer rules. This patch does not clear a whole substitution's taint boolean.

## Producer admission

* VariableValue::push returns before recording an empty string. It inserts any required comment separator before capturing the tainted start, so the separator itself is excluded; then records the actual appended bytes.
* AttrTaint::new_fully_tainted constructs [0,end), including possibly [0,0).
* do_substitute_chunk's optimized whole-reference branch records [start,substitution length). Its public internal caller uses start0. Recursive fallback calls pass attr_taint=None, so nonzero fallback starts do not reach that recording path. Empty whole substitutions can therefore record [0,0), not an arbitrary interior point.
* The two URL span callers are CssUrl::parse_with_cors_mode and ImageSetItem::parse. Successful URL/string tokens occupy nonzero source widths even for an empty decoded string. Their start can include skipped whitespace; this proposal does not shrink or normalize their spans. No claim that whitespace-taint false positives are universally fixed.

In the confirmed case, the URL starts after image-set( and ends just after the closing quote. The following typed resolution is tainted and begins at that exact end. String/Dimension token categories do not require a serialization comment. The one-space variant separates the ranges and already passes.

## Preservation and regression gates

Keep the five existing diagnostic cases unchanged. They include direct literal adjacency, typed resolution calibration, actual attr URL rejection, and whole custom-property taint rejection. Add helper-level empty/containment/disjoint/multiple-range checks if a native unit-test location is selected; the artifact checker only validates the mathematical range examples and exact source delta, not Rust execution or a universal compiler theorem.

Root should execute the candidate against these five tests and the existing attr-security controls. Given the touching fix is permissiveness-changing, review all URL callers and substitution producer boundaries before acceptance. No global taint propagation, metadata equality, interpolation, grammar or defaulting behavior is changed. No isolated upstream build or novelty claim is made. Native patch applies to the retained source; independent upstream applicability is a root gate.

## Performance

The loop and allocation behavior are unchanged. Each range uses two min/max selections and one strict comparison; generated branch/conditional-move behavior is compiler-dependent. There is no performance benchmark in this capsule. This is a small bounded extra comparison relative to the two-comparison original, not a measured zero-cost claim.

## Prior issue

Bug1997583 introduced partial-taint checking and is resolved Firefox152. This is a boundary-condition follow-up candidate against that retained implementation, not a claim that the feature was unimplemented. Source discovery and specification trace are in the separately sealed audit.
