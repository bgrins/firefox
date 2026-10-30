The current branch reproduces a min/max simplification defect involving infinite font-relative lengths. This is a source-guided finding, not a formal-verifier discovery or an accepted fix.

At font-size zero, infinity * 1em is NaN. min(-1px, infinity * 1em) must therefore retain NaN until the top-level calculation becomes zero. Instead, the simplifier chooses -1px before the font size is resolved. max(1px, -infinity * 1em) similarly chooses 1px. Both argument orders fail. Same-unit comparisons also discard NaN; adding 1px outside the comparison exposes the difference between an internal NaN and an ordinary zero.

The 18-case WPT collects all three observations before asserting, changing font size from 0px to 16px and back. Eight targets fail in the authenticated branch run; ten controls pass and the harness ends OK. Controls cover finite relative terms, absolute infinity, clamp, same-sign cross-unit comparisons that already defer, font-context changes and explicit NaN propagation. These observations do not instrument the exact native execution path.

Root ran session37950, launchbb5bfe, terminald5db3b with owner exit0 and WPT exit1. The latter reflects the eight observed failures. Independent raw replay1caeaf/0 verifies the complete roster, matching application metadata and PRE/POST state. The owner joins213 native/build pins to the existing pow build, uses harness HEAD ecfe313d582a335c04d80bfd360fd3a591defdb7 and binds build revision20ab7e723b663c0f78c8490e60a6fccc5e65cc99. It preserves the accepted pow source, held provider, canonical state and binaries. No source installation, build, candidate comparison or native acceptance occurred.

The exploratory System Firefox158 observations are saved separately. That browser was not authenticated as the branch build. Its owned tab and temporary elements were removed. The branch WPT run supplies the authoritative reproduction.

CSS Values4 special-value and comparison semantics provide the oracle:

- https://drafts.csswg.org/css-values-4/#calc-ieee
- https://drafts.csswg.org/css-values-4/#comp-func
- https://drafts.csswg.org/css-values-4/#calc-simplification

The local MinMax simplifier checks coefficient NaN, compares leaves, and replaces the node with a selected child. Specified Leaf::compare can order Length leaves by coefficient sign even across units. Unlike the existing Clamp path, MinMax does not guard unresolved relative infinity. The nine-line artifact proposal defers before replacing the winner when any child is an infinite noncanonical leaf. It leaves the existing explicit-NaN early returns intact. This is conservative and can change specified serialization; native compilation and broader regression validation remain pending.

Deduplication against all149 accepted ledger entries found no MinMax relative-infinity repair. Related fix20 repairs Clamp NaN folding; fix119 preserves nonfinite intermediates during relative-length conversion; fixes144/145 address Round. Bounded public searches and source inspection do not establish that no existing external bug report covers this issue. No new bug ID or accepted count is assigned.

The separate Lean companion proves twelve scoped laws and rejects four false controls. It models independent extended-value semantics and an abstract coefficient-based selector, including a sufficient defer condition and zero/positive basis changes. It does not prove the full native comparator, IEEE arithmetic, n-ary behavior, parsing or invalidation. Its canonical library coverage increment is zero.

Static fixture validation registered18 unique callbacks and passed WPT lint. The first isolated/no-site attempt failed before lint because PyYAML was unavailable; rerunning with the configured virtualenv site packages succeeded. WPT's temporary-root Git diagnostic did not prevent lint or manifest generation. Browser owner v1 was never executed: v2 replaces its authored raw-SHA1 manifest entry with the actual WPT-generated Git-blob entry while preserving the executable bodies.

Next: validate the exact guarded candidate through a reversible local build/browser comparison, then run a broader min/max/clamp regression selection. Only successful final installation/build/WPT validation can precede a standalone native+WPT commit. Contextual easing separately still needs its prepared six movement/ownership cases and a disposition for the animation-only refresh boundary; its prior315-case comparison and Servo checks remain valid evidence within their scope.
