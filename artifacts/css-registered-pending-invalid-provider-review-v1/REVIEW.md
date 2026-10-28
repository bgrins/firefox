# Recursive registered-provider default review

The sealed proposal `css-registered-pending-invalid-provider-repair-v1` remains uncompiled and unaccepted. This was a bounded read-only source review, not native execution or a proof of correspondence. All 19 payloads were authenticated (a2becc/0); source reads were b7c116/0, 0c87c0/0, 752a79/0, 8079aa/0 and 0527b4/0.

The extracted ordinary invalid/default and CSS-wide helpers preserve the inspected original branches: inherited-value cloning and taint, root initial selection, default taint for recomputed initials, complete CSS-wide parsing, initial remove-before-insert behavior, and INHERITS_RESET_STYLE. No concrete regression was found in this extraction.

## Incomplete missing-provider path

In substitute_one_reference, recursive substitute_internal errors still return None before registered_default is called. A registered provider such as `--mode: var(--missing)` can consequently be treated as absent by an early `writing-mode: var(--mode, horizontal-tb)`, although its eventual registered initial is vertical-rl. This is a concrete source-path omission in the proposed repair, not an executed reproduction or a claim that the patch introduced it. Test it with and without the consumer fallback, in both declaration orders, using the existing line-height readiness trigger. Also cover inherited defaults and the root-element case.

Do not turn every recursive error into a default indiscriminately. A seen-name cycle and an ordinary missing reference are different causes. All actual SCC participants must still be invalidated; returning an inner initial must not break discovery of the cycle or allow an inner fallback to rescue a poisoned outer context. Self and mutual registered cycles, including inner fallbacks and a nonparticipant consumer, need explicit regression checks. Unchanged local seen guards alone do not prove whole-cycle equivalence.

## Early initial computation

The new recursive path calls compute_value for a noninherited registered initial without first establishing the initial's intrinsic context dependencies. The later ordinary handler previously ran at its resolver position. Color-scheme-sensitive initial values are a concrete readiness concern in this source route; no observable new color regression was demonstrated in this review. Preserve this as an acceptance gate rather than claiming every computationally independent initial is context-free.

## Minimal next validation

Keep both exact original 16-case readiness fixtures and the proposed 32-case supplement. Add missing-reference defaults, inherited/root cases, typed-attribute invalid/missing providers, self/mutual cycles with fallback, and a color-scheme-sensitive initial with a settled direct calibration and mutation. A controlled candidate build is useful; it does not by itself settle these semantic gaps. No upstream/release browser behavior, security impact, canonical Lean coverage, or native refinement is claimed.
