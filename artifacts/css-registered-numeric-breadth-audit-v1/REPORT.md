# Registered numeric dependency breadth audit

Recommendation: group the numeric syntaxes under one root-cause report/fix. Expand the current repair before acceptance if controlled original/candidate probes confirm the shared cases. Do not count integer, angle, time, resolution, percentage, alternatives or repetition as separate discoveries merely because the syntax differs. Browser hypotheses remain unrun.

## Confirmed source paths

The captured `visit_value_references` is registration-agnostic: it accumulates lexical FONT/LH flags, resolves selected providers, and can carry unused-fallback units. `traverse` then adds non-custom edges for any typed registration with those flags. A var-containing declaration enters traversal independently of its initial type mask. The new `is_exact_number_registration` gate only repairs one unmultiplied Number descriptor. Other scalars, alternatives and lists skip refinement while traversing the same shared code.

Thus the same false-edge mechanism is source-reachable for a ready integer 5 with unused 1em fallback, and for ready angle/time/resolution/percentage values consumed by compatible font-size expressions. This is confirmed shared code reachability, not a browser reproduction or proof of every resulting serialization.

The pinned specified calc source retains admitted trees for number, angle, time, resolution and percentage. The pinned Integer wrapper and current Searchfox wrappers resolve these trees using computed context. A final non-length type can still contain an em/px ratio. The ordinary cascade's initial filter uses descriptor LENGTH plus the proposed exact-number exception; current upstream dependent_types marks the other numeric types empty. This identifies noncyclic math scheduling probes. Upstream wrapper captures are not claimed identical to the checkout.

CANDIDATES contains 17 proposed controls: two per scalar family (unused relative fallback and noncyclic 20→30 math), four alternatives/repetition cases, two later-list-member cases, and an integer-provider-to-number chain. Every syntax needs a literal registration/consumer calibration before interpreting failures. Selected-invalid and wrong-primary-no-retry controls distinguish grammar behavior. No self-font numeric default is asserted.

## Scope and reusable architecture

The number specialization is not an architectural dead end. The shared boundary already selects settled providers, parses the complete real registration, retains an owned specified value through SCC settlement, and converts once. Extend that boundary, rather than globally deleting flags or labeling every numeric result LENGTH.

For alternatives, collect from the actual first completely matching component. For repetition, collect every admitted component; a later list item can require font context. Any unsupported child must preserve unknown. Number and Integer expose as_calc; the examined angle/time/resolution/percentage wrappers hide their NumericUnion, so small AST-access helpers or wrapper-local collectors are needed. Never substitute scalar get/resolve calls. Preserve each type's original clamping, rounding and computed conversion. Percentage-hint semantics require separate review before treating Percentage leaves as context-free.

A number consumer can receive an already incorrect value from an excluded typed provider: integer --i:calc(1em / 1px), number --n:var(--i), explicit font-size:20px, width:calc(var(--n)*1px). The current number preparation cannot repair the provider's earlier computation. This is a preexisting shared scheduling gap, not evidence of a newly invalid owned cache. Do not present the patch as fixing arbitrary typed provider chains.

## General non-universal preparation: necessary limits

Owned selected substitution plus real grammar admission can plausibly be generalized beyond numeric-only descriptors, but selected-token flags alone are NOT a conservative replacement for every registration. Concrete source evidence: find_non_custom_references adds COLOR_SCHEME for Color descriptors, whereas the captured token/reference parser does not populate that flag. A selected system-color value can therefore require color-scheme readiness even with no lexical unit. Preserve type-implied dependencies as well as selected-token inventory—preferably from the admitted component, conservatively from the descriptor until supported semantics exist.

For an unsupported AST, scanning the selected substituted tokens removes the original unused-fallback contamination, but may still conservatively include unchosen nested math/anchor/function branches and cannot discover implicit type dependencies. This is a fallback approximation after successful grammar admission, not a semantic completeness proof. Invalid or CSS-wide outcomes use their existing handlers and should not schedule rejected expression units.

The graph must settle providers before preparation; an open SCC or pending provider is not invalid. Retained specified values must still be discarded on cycle exits, with computation/publication after settlement. Substitution reads attributes/environment and records dependencies; generic parsers can carry URL/taint/property-context behavior. Review those paths before broad early parsing, preserve full taint and namespace/URL arguments, and do not infer that parsing is effect-free. A broader numeric-only first expansion avoids silently asserting all URL/image/color semantics are covered.

## Packaging and evidence boundary

If calibrated paired probes confirm these shared paths, extend the same standalone native fix and WPT. Keep previous number-only artifacts/results as historical evidence when versioning. A separate report is warranted only for an independently demonstrated mechanism or distinct unresolved policy, not syntax count. If expansion is deferred, explicitly document incomplete family/provider coverage on the existing report.

The inspected native proposals, collector and descriptor parser are pinned in REFERENCES. Six untouched APIs were discovered/read through Searchfox and retained with hashes; no revision identity is invented for those current upstream captures. No build, browser, live source, Git state, epoch, canonical Lean file or ledger was modified. Accepted-bug and canonical coverage increments are zero.
