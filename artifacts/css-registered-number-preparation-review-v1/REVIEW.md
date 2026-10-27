# Registered-number preparation review

No blocking source defect was identified in the sealed ordinary and live proposals. This is a bounded source review, not native compilation, runtime validation, a cycle-policy approval or acceptance of a fix. The reviewer authored the separately bound collector; this review supplies independent scrutiny of preparation/integration, not an independent second implementation of that collector.

## Readiness and cache lifetime

`visit_value_references` checks the actual referenced node after `visit_link`. Its boolean remains false if any visited primary is still represented by a nonempty `var_info[index].var`. A missing map entry is not the readiness test. In the live variant a pending provider is checked before the map shortcut, and its demand propagates through `?`. Missing and already computed providers can safely have no graph index. If a primary was once open but later closes during the visit, the retained false result is conservative: the optimization is skipped.

Preparation retains an owned specified AST, not a borrow of the substitution map. All visited primary providers have settled before it is built. Subsequent non-custom recursion can reveal a cycle involving the current property; the local prepared result is then dropped on the lowlink return or the in-loop return. Only the SCC root's noncyclic path applies it after popping the stack. Closed providers cannot subsequently join that SCC. This prevents early publication of a value selected against an unresolved custom-property cycle.

The visitor still contains its preexisting conservative fallback traversal when a primary is unresolved, including the old comment calling such a primary invalid. The new readiness guard prevents that old classification from authorizing preparation. This proposal does not prove the existing visitor's entire cycle/fallback policy.

## Parse, compute, effects and defaulting

The original registered conversion is `Substitution::into_value` → `compute_value` → `SpecifiedRegisteredValue::compute`, where compute is parse followed by `to_computed_value`. The extracted path passes the same registration descriptor, URL data, namespace argument (`None`), computational-dependence permission, property identity and fully tainted substituted range. It retains that parsed value and performs the same conversion once at apply time; the resulting attr-tainted bit is ORed with the substitution bit just as before.

`Invalid` invokes the existing invalid-at-computed-value handler. It does not retry a var fallback after the selected provider fails number grammar. `CssWide` invokes the extracted existing keyword match, including inheritance flags and the preexisting revert policy. Empty scheduling references on those outcomes are appropriate because the rejected numeric expression is not computed. Whole-keyword parsing behavior is unchanged; the proposed inherit-extra controls check that boundary.

Early substitution still queries attributes, consults environment values and parses typed attribute values. Therefore preparation is not effect-free in the sense of doing no reads or dependency tracking. The patch reuses the original helpers and tracker and avoids numeric `to_computed_value` until settlement. Attribute reads made for a later-discarded result may conservatively remain tracked. This review found no extra DOM mutation, value publication, early font conversion or dropped final taint propagation in the new path. It is not an exhaustive proof of every parser side effect.

## Live demand handling

The live helper distinguishes substitution Invalid from Demand. Provider/attribute demands escape without becoming cached Invalid. `PreparedRegisteredNumber::apply` checks represented font/line-height requirements and their transitive prioritary dependencies before converting or inserting the value. Unsupported collector results use a selected-token conservative inventory for that check; graph traversal independently retains its original accumulated references. Failure of that conservative parse becomes ContextPreparation demand, not empty references.

A demand after SCC popping consumes/drops this traversal-local prepared result; the caller must retry through the existing demand protocol. No persistent prepared cache was introduced. The broader pending resolver's temporary maps/effects and retry/publication transaction remain responsibilities of that preexisting prototype and require its native tests. A successful ordinary WPT run cannot validate those obligations.

## Validation gaps and next gates

The 52-target WPT fixture exercises the key selected-unused-fallback bug, invalid admission, real custom/attribute cycles, CSS-wide values, order and mutation. Its two math mutation tests cover a current-font em numerator with a px denominator. They do not directly cover admitted lh, root-font/root-line-height cases, inverse relative denominators, every eager math operand, unsupported collector None, or pending-provider/prioritary/attribute retries. The collector's 16 proposed controls are unexecuted and must not be reported as native coverage.

Before acceptance, build and run the clean-HEAD original/candidate comparison, retain exact target/regression identities, then separately validate the restored live overlay and actual pending host tests. Include at least a successful noncyclic lh calculation, a root-unit mutation, inverse-relative division, and an unsupported-node conservative control in follow-up native coverage. Numeric self-font-cycle defaulting is explicitly unresolved by the normative work; the exact-number graph prefilter can change that behavior, so preserve observation-only results and obtain a policy decision before claiming the change fully settles those cycles.

The three input manifests and every listed payload were authenticated from artifact copies only. No live source, build, browser, epoch, index or HEAD was queried or modified during this review. No source patch is altered by this report.
