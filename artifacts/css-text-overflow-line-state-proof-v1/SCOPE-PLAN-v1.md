# Ordinary line-state companion plan

Scope accepted from the root design, 2026-10-18. Preserve the frozen original
and candidate source. This artifact changes no native/WPT/Git state and launches
no browser or shared build.

Extract complete ProcessLine, ExamineLineFrames, SetupString, subtree/edge
analysis, IsAtomicElement, IsFullyClipped, both inflation helpers, the relative
geometry wrapper, exact Marker and alignment/clip accumulator declarations.
A source-bound observer insertion after each subtree-analysis pass records its
inputs/results; removal must recover the exact extraction. No observer changes
production decisions. Caller/factory and output routines stay pinned and audited.

Owned adapters provide frames with valid derived types, stable style/string
storage, line geometry, scroll/float/snap observations and explicit text-cluster
advances. No provider supplies overflow/retry success. Exact native logic decides
those outcomes. Logical coordinates are primary; horizontal LTR/RTL physical
conversion is independently checked. Full shaping/reflow/vertical conversion and
display-list rendering remain provider assumptions. Output methods record both
list calls, marker decisions, intervals and complete marker states without
mutation. Every result includes measurement count and per-attempt traces.

Python independently classifies interval/cluster visibility and defines retry
state transitions over those observations. Compare full states/traces for
original and candidate; ordinary reuse and fresh seeded-state runs separately.
Clamp records exercise full native branches diagnostically, without a universal
clamp-isolation claim. Own all pointed-to values before connecting pointers.
Compile/run with UBSan and explicit lifetime diagnostics; no sanitizer timeout
counts as success.

Lean proves entry canonicalization, retry reset preservation, finite ordinary
reuse versus fresh seeded state under deterministic stable-measurement kernel
premises, and bounded width/priority lemmas. Concrete executable model results
are compared with native/Python where their boundaries agree. This is not a
universal native refinement theorem. Audit every theorem and execute semantic
counterexamples for every theorem-elided mutation, besides proof rejection.

Native semantic mutants must compile and exit zero on the declared corpus.
Assertion-invalid or nonterminating trials remain diagnostics and cannot be
counted as killed semantic mutants. Pin source closure, actual selected compiler,
SDK/tool identities, extraction ranges and every replay input. Bind root WPT
identities only when supplied. Freeze after full producer replay.
