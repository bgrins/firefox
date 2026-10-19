# Animation endpoint metadata repair

## Acceptance

The three-source repair and six-case CSS-wide WPT are accepted for local
commit. The stack patch has four files. The upstream alternative has five,
including the necessary shared-map insertion prerequisite from fix76.
Neither patch includes formal tooling or research documents.

The root reviewed the full new Lean model, shape proofs, retention/history
proofs, witnesses, executable mutation driver and source mapping, separately
from their author. Root also read and replayed the independent native/test
review. The additional native scan is confined to UpdateProperties; global
AnimationValue equality and other comparison consumers are unchanged.

## Browser and build evidence

The paired driver completed a successful local build and 101 passing subtests
with twelve OK harness results. Raw event rows match the retained receipt.
Both same-payload directions fail at the final URL-taint assertion before the
repair and pass afterward, in both the CSS-wide landing test and the separate
typed-keyframe diagnostic. All other 97 identities retain PASS. The baseline
is explicitly joined from runs on identical binaries, not represented as one
101-case invocation. The existing setKeyframes test adds 80 passing subtests
and one OK harness, including empty replacements and immediate ordinary
property updates. Source and binary pins remained stable during each run.

The older attr-security test contributes 32 reported passes, but 29 contain
conditional assertions. Those are not counted as 29 unconditional security
checks. The new CSS-wide cases calibrate parent payload and taint, initial and
final effect payload, raw keyframe replacement, fresh effects, literal URL
acceptance and different-payload replacements. Constant endpoints avoid a
mixed-provenance interpolation assumption.

The build exited zero and reports success. Four build-monitor export KeyErrors
and compiler warnings are retained in its log; these did not prevent compiling
or linking the generated FFI. Format and scoped lint exit zero, with one lint
warning. Formatting wrapped one C++ expression across two lines. The exact
before/after substitution is checked in FORMAT-TRANSFER.json; no token,
directive, string or comment changed. The original compiled source and proof
binding transfer through this sole whitespace change. No second native build
is claimed for formatting.

## Formal scope

The root's fresh kernel replay passes 25 exact theorem/axiom audits and two
compiled semantic mutants. Missing either endpoint comparison produces the
intended executable discrepancy in both replacement directions. Ordinary
comparison derives array and segment shape before the added indexed reads;
the scan is equivalent to an independently defined endpoint-bit projection.
Retention preserves that projection after every finite modeled replacement
history and every prefix. Arbitrary payload comparators are permitted, so
these theorems do not establish payload correctness or full observational
equality.

Native identity must imply consistent custom-property classification. The
property/provider-to-custom-variant association, pointer lifetime, machine
representation, faithful native traversal, raw-keyframe computation, call
delivery, base-style scheduling, interpolation and eventual publication are
explicit admissions. Source hashes establish identity, not automatic C++ or
Rust verification. URL-data equivalence and the complete attr/substitution/URL
pipeline remain open. The independent source review supports these local
bridges but does not turn them into kernel proofs.

## Standalone and attribution

The CSS-wide fixture uses existing initial/inherit computed providers and
avoids fix70's typed keyframe construction repair. Upstream map insertion can
discard clean initial A over inherited tainted A; the standalone patch includes
only the metadata-aware do_insert check needed to prevent that. The separate
universal cascade shortcut from fix76 is not required by this fixture.

Root verified both patches against actual Git objects using temporary indexes,
including exact changed paths and candidate blobs, and exact reverse-to-base.
The upstream alternative has not had an isolated upstream build/browser run.
Shared-tree tests alone do not prove absence of every upstream interaction.

Discovery came from source investigation of metadata omitted by equality and
browser reproduction. The new Lean component followed that finding and checks
the local repair obligation; it did not automatically discover the browser bug.
EnsureBaseStyles has a separate scheduling hypothesis under investigation and
is deliberately outside this accepted endpoint patch.
