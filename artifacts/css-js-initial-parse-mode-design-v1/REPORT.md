# JS initial parsing with retained calculation trees

A JS-only mode is feasible at a concrete native boundary. It is not yet a sound registration validator. This package proposes an interface and identifies the remaining admission obligations; no source patch is applied, compiled, or claimed production-ready.

`ParserContext` already reaches every `CalcNode::parse_*` wrapper. The wrappers invoke context-free `into_length`, `into_length_or_percentage`, `into_number`, `into_percentage`, `into_angle`, `into_time`, or `into_resolution`; each unconditionally calls `simplify_and_sort`. The numeric tree is still available immediately before those calls. The normal registered syntax parser constructs its own ParserContext and iterates complete syntax alternatives. This is a suitable place to opt into a separate parse purpose without changing global `CalcNodeLeaf::sign_from` or ordinary steps/subgrid parsing.

## Proposed interface

Add a parser-context purpose with default `Ordinary` and a separate `ScriptInitialAudit` value. Keep it separate from `DISALLOW_COMPUTATIONALLY_DEPENDENT`: the latter rejects grammar candidates before normal alternative selection. An inactive registered-value entry point can thread this purpose into its locally constructed context. Existing callers remain Ordinary.

Thread the purpose explicitly through all seven numeric finalizers. In audit mode, retain the complete numeric tree before simplification while still doing the existing numeric-type validation and storing the same clamping mode. Do not change the generic simplifier. Public/non-parser finalizer callers must continue selecting Ordinary explicitly; the captured anchor fallback call also needs its real context propagated. This is not a proposal to switch off all simplification for every CSS parser globally.

For diagnostic development, first perform the existing normal complete grammar selection and record the selected syntax component. Attempt an audit parse of exactly that component, never the remaining alternatives. Return either an owned retained value plus audit, or an explicit `SelectionMismatch`/`Unresolved` diagnostic. A different successful branch, early rejection, or unresolved scalar requirement cannot be turned into SyntaxError or successful independence. This development interface is intentionally not an executable JS acceptance algorithm.

The eventual production path must establish that the retention mode preserves the normal grammar's selected representation, including nested parser choices, then retain that owned AST through the registration cache as detailed in the referenced RETENTION.md. A second parse used only as a diagnostic is not the proposed final cache architecture. The `Option<Box<SpecifiedRegisteredValue>>` field, script-versus-rule constructor distinction, outer ToComputedValue conversion, and ordinary deep memory accounting remain applicable after a valid selection-preserving implementation exists.

## Why this is more than disabling one fold

The captured generic simplifier has at least three relevant branches:

* Sign calls `sign_from`, which uses `unitless_value`. This is already held fix120, with unresolved contextual integer-consumer admission regressions; no revival or new discovery is claimed.
* Atan2 checks `is_same_unit_as` and then both `unitless_value` coefficients, producing an angle. It does not require canonical values. A zero em basis is a concrete source/spec counterexample candidate, separated into the atan2 probe artifact.
* Progress checks same units across all three leaves and computes a dimensionless result from their coefficients. A zero basis can collapse the interval. This is a source-audit lead, not a separately tested or counted bug.

By contrast, inversion folds a leaf only when its numeric type is Number; ordinary same-unit arithmetic often retains a dimensional leaf. Clamp and other comparison/arithmetic branches can select or combine leaves and need individual equivalence reasoning, particularly for NaN/infinity. The presence of canonical-value guards in some branches does not establish that every other branch preserves context. This package makes no exhaustive all-operation soundness claim.

Retaining a complete unsimplified tree would preserve these numeric operands at this boundary. It does not prove nested grammar selection, later component conversion, or nonnumeric parsers preserve them. The existing Number wrapper retains a CalcNumeric box, but other consumers call scalar accessors or normalize colors. Those consumers require an explicit admission audit before activating this mode across images, colors, transforms, and lists. A failed audit parse is not permission to fall through to another syntax alternative.

## Zero/cancellation and failed alternatives

Do not infer dependence merely from the retained tree containing an em/cqw leaf. The previous erasure report leaves zero-times/cancelled expressions and permitted simplification semantics unresolved. A retained tree is evidence for analysis, not a certificate of dependence. Equal light-dark branches and symbolic currentcolor likewise require their own semantic rules. Ratios need zero/NaN/signed-zero handling; ordinary algebraic cancellation is insufficient.

A side journal on ParserContext would avoid changing normal parser results but would collect failed speculative parses too. Rolling it back only at the top-level syntax-alternative boundary is insufficient because nested parsers also backtrack. No such journal should authorize a rejection or acceptance without ownership/transaction semantics for the actually selected nodes. Merely OR-ing encountered dependency bits repeats the discarded-alternative contamination problem.

The minimal next implementation experiment is an inactive purpose-threaded numeric parse entry point with comparison controls for selected scalar and list ASTs, followed by explicit nested-consumer controls. Keep the diagnostic unresolved until selection preservation and independent-value semantics are established. Current ordinary parsing and held120 remain unchanged.

## Evidence and limits

Searchfox discovery located the upstream context-free finalizers and generic simplifier; actual local source bodies were captured with SHA256 before analysis. Upstream line offsets differ from the branch; these are local-body pins, not pristine-upstream equivalence claims. Relevant reads:759eb0/0,4cce77/0,e6645e/0,f158b2/0,836b0a/0,634afb/0,dbc93f/0,f4befa/0. No build, browser, runtime-control, index or canonical source mutation occurred. Only this artifact and the separate bounded probe were written.
