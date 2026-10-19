# Pseudo-scroll timeline source, snapshot, and sampling proof companion

Producer evidence for the approved full scope in `APPROVED-SCOPE-v1.md`.
This companion verifies a declared source-selection/provider model and checks
its connection to complete extracted native functions. It does not prove all
CSS scroll-timeline conformance or browser rendering.

## Reproduction and file classes

`SOURCE-MANIFEST-v1.json` enumerates every required source input. Authenticate
its digest against the producer handoff, then run:

```
python3 -I -S verify.py --expected-manifest DIGEST
python3 -I -S verify.py --expected-manifest DIGEST --clean /absolute/new/output
```

`--clean` copies only those inputs into a fresh `/private/tmp` directory. It
executes under a macOS sandbox denying network and Firefox checkout file reads,
except the explicitly declared Lean toolchain directory. Ancestor-path metadata
is allowed solely to locate that toolchain; checkout file contents remain denied. It rebuilds both native
variants, runs all corpus comparisons and mutants, checks all Lean theorems,
executes Lean counterexamples, and audits theorem axioms. The output directory
contains the copied source closure, command statuses, observations, traces,
mutant witnesses, axiom inventory, and `CLOSURE-RECEIPT.json`.

`--live /path/to/firefox` optionally checks only the candidate native source
pins. Historical browser binaries are never compared to current binaries.
`development-*`, `__pycache__`, and clean replay output are generated evidence,
never replay inputs. The verifier authenticates all sources and toolchain inputs
before compiling/importing local helper source; it never imports local pyc files.

`TOOLCHAINS-v1.json` pins the Lean distribution, Python interpreter/stdlib,
compiler, SDK settings, and C++ header dependencies. The macOS runtime/frameworks
and declared Xcode compiler/linker runtime remain platform dependencies. This is
an isolated source closure, not a proof of the compiler, OS, or toolchain.

## Exact native boundary

Each variant executes 24 complete lexical extractions: five declarations or
inline members, 16 ScrollTimeline definitions, and three provider definitions.
See generated `*-bindings.json` for signature, full-body SHA-256, character and
UTF-8 byte spans. Extraction preserves bodies, declarations, guards, branches,
loops and order. No signature, namespace, access-label or semantic statement
rewrite is applied to an extracted unit. An outer adapter class supplies the
surrounding declarations and exposes its own harness accessors. Inner private
labels remain intact. Every emitted extraction is checked against its pinned
origin bytes and appears exactly once in the translation unit.

This includes all ScrollerInfo factories and source selection, full nearest
ancestry traversal and pseudo conversion, actual timeline factories/constructor,
ComputeSnapshot/GetSnapshot, complete StateSnapshot, both layout-utils providers,
UpdateCachedCurrentTime, CurrentTimeData equality, the complete subscriber loop,
ComputeTimelineData and both public current-time getters. Native assertions are
enabled; original traces include the extra host-frame query in its assertion.

Owning C++ document/element/frame objects are separate. Host, before, after,
primary and scroll-target records remain independently addressable; primary and
scroll roles may legitimately refer to the same frame. All worlds remain owned
through a scenario. Deletion/recreation tests replace lookup records/generations;
they do not prove reclamation or dangling-pointer safety in Gecko. Allocation,
RefPtr lifetime, registration and endpoint allocation are external adapters.
`Maybe` moves clear the source, following the retained `mfbt/Maybe.h`; the
standard optional adapter supplies explicit equivalent move operations.

Complete caller/impact files are retained and their relevant definitions mapped
by the replay's boundary inventory. WillRefresh, UpdateIfStale, manager name
lookup/construction, registration and ViewTimeline sampling are outside the
universal sampling entry point. Existing browser ViewTimeline controls belong
to root's separate acceptance gate.

## Independent definitions and typed boundary

`oracle.py` defines source selection by collecting eligible ancestry before the
root sentinel, resolves providers from raw records, and constructs observations
directly. It does not import the native-shaped interpreter, Lean, generated
results, or browser expected fields.

`Timeline.lean` independently defines declarative and native-shaped source,
frame, snapshot, cache and notification algorithms. `Trace.lean` executes the
native provider ordering and both frame resolutions. `native_model.py` is a
separate trace interpreter. Native output agrees with the Python oracle's whole
structural projection and with both trace interpreters, including receiver IDs,
operations, arguments and values (`TRACE-SCHEMA-v1.json`). Writing-mode trace
values retain the supplied orientation and reversal fields, not Gecko ABI bits. Lean's trace erasure agrees on the bounded
corpus; no universal trace-erasure theorem is claimed. Universal semantic
correspondence is between the separately defined Lean algorithms.

`Typed.lean` is the authoritative Lean input boundary. It uses nominal DocumentId,
ElementId and FrameId types plus host, pseudo, primary and scroll role wrappers.
Typed world records are parsed before algorithms run. Invalid owners, aliases,
missing frame roles and non-scroll frames used as scroll roles are rejected.
World erasure is lossless under the explicit one-document ownership premise;
round-trip and element/frame/primary/target provider lemmas prove this bridge.
Source, resolution, sample and finite-sequence agreement transport across it.
The encoded algorithms use natural IDs to keep graph recursion and finite-domain
reasoning small; the execution boundary never accepts an unconstrained encoded
world directly. A primary/scroll role conversion retains the same underlying
FrameId. No false disjointness premise separates legitimate frame aliases.

## Universal results and hypothesis audit

The generated `theorem-inventory.json` and `axioms.log` list every exported
statement and its complete hypotheses. No sorry, admit, unsafe proof shortcut,
synthetic expected-answer axiom or native_decide is used. Only Lean's standard
`propext`, `Classical.choice` and `Quot.sound` foundations are allowed by the audit.

The dependency structure is:

- Raw parent chain -> declarative filtering/native recursion correspondence ->
  ranked traversal completion -> nearest/all-source correspondence.
- Independent provider resolution + axis correspondence -> snapshot agreement.
- Snapshot + frame resolution + notification-list agreement -> sample agreement
  -> induction over arbitrary finite resampling sequences.
- Raw frame-mode mutation -> unchanged provider resolution -> named host-mode
  snapshot/sample/progress noninterference -> two-run finite-sequence theorem.
- Physical axes/equal modes/inactive guards -> repair preservation -> finite
  sequence preservation. Original and repaired raw traces may differ.
- Typed round trips/provider correspondence -> transported source/resolution,
  sampling and finite-sequence contracts.

`Valid` bounds source kinds/axes and requires a null frame with no target/shell.
Core record theorems hold for a wider integer domain than ordinary browser
geometry. `Path` and its explicit length bound discharge native traversal fuel
for finite acyclic parent chains; typed `Admitted` includes this ranked provider
premise, typed ownership and role validity. The corpus validator checks every
ancestry for cycles and the rank bound. Arbitrary cyclic graphs are not a native
termination claim.

The mode mutation premise constrains every raw frame record: only the designated
host primary frame's orientation can change. It does not assume an expected
source/axis/cache answer. The resolved frame must differ from that primary
frame. The named-source theorem therefore covers the non-root pseudo repair
under independent pseudo/scroll identity and stable providers. Physical axes,
direction-only changes, and APZ-enable changes have separate noninterference
lemmas; APZ enable can change snapshot APZ state while leaving time unchanged.

Clearing/reconstruction proofs connect absence, cache replacement, return flags,
subscriber notifications and getters. Inactive/unavailable samples clear time
and return old presence without notifications. New activity/extent change
notifies both methods on every subscriber; position-only changes do not.
A new valid sample computes data from current providers regardless of old cache.
Named/provided/self preserve the host/pseudo pair; generated and ordinary nearest
pair conversions have explicit identity lemmas. Public source exposure is the
host convention, separately labeled from normative logical-axis meaning.

## Corpus, mutations and numeric scope

The deterministic generator covers all five source kinds, ordinary/before/after,
independent host/pseudo/scroll modes, four axes, four availability sets, and
zero/one/several subscribers. It adds root standards/quirks provider ownership,
root substitution/fallback, pseudo/root diagnostics, nearest distractors and
missing-provider boundaries, delegated targets, APZ short circuits, axis/source
replacement, repeated samples, disappearance/recreation, same-data new frame
generations, orientation/direction changes and asymmetric geometry.

Other generated pseudo kinds have bounded identity controls. View-transition
names and arbitrary named transition pseudo lookup are unsupported in this
model; the full native conversion branch is retained, with its nameless control.
The ordinary/before/after theorem domain is not expanded by those controls.
Root-generated pseudo classification and the existing nearest single-axis policy
gap are retained behavior, not accepted new conformance claims.

The replay executes all 11 approved native semantic mutant families. Each has a
compiled executable, zero process status on its admitted witness run, a structural
mismatch against the independent baseline, an executed corresponding Lean
witness, a preservation control, and an exact counted reversal. Candidate native
output is freshly replayed between batches. The nonzero-start mutant uses a
positive remaining interval; an earlier diagnostic reaching zero after that
intentional fault is retained in development evidence and is not counted as a
successful semantic witness.

Signed offsets are int32 excluding INT_MIN before abs; extents are nonnegative
int32, and selected getter extents must be positive. Ordinary cases also require
available directions to match positive extents and abs(offset) <= extent.
Explicit inconsistent-availability and out-of-range diagnostic cases are labeled
outside ordinary geometry. Invalid cycles, missing required targets, broken
pseudo backreferences, INT_MIN and zero selected extents are rejected before
native execution. Typed-owner/role rejection cases are separate from mutants.

Native integer records compare exactly. Getters execute their actual double
expressions and both Typed OM/fallback dispatches. Payloads match Python binary64
operations exactly, with a separate rational error check of at most two ulps;
dyadic cases require exact rational equality. Lean proves the rational selected
record projection and its preservation, not IEEE execution, TimeDuration internal
quantization, CSSUnitValue allocation, RTL scroll-origin policy or CSSWG #12893.

## Specification and external obligations

Pinned primary drafts:

- Scroll-driven Animations 1: logical axes use the scroll container's writing
  mode; unavailable relevant overflow makes time absent. Anchors
  `scroll-timeline-axis`, `scroll-timeline-progress`, `scrolltimeline-interface`
  and `event-loop` in `source/spec/scroll-animations-1.html`.
  <https://drafts.csswg.org/scroll-animations-1/>
- CSS Pseudo 4 generated-content boxes:
  `generated-content` in `source/spec/css-pseudo-4.html`.
  <https://drafts.csswg.org/css-pseudo-4/#generated-content>

Actual root/fieldset scroll-target providers, used writing modes including HTML
body propagation, layout geometry, generated boxes, refresh delivery, reentrancy,
real allocation/lifetime, compositor/APZ behavior and rendered animations remain
external obligations. Inputs supply raw graph/style/geometry facts, never expected
axes, selected source winners or expected current-time records.

Root owns paired browser acceptance and the independently landable native/WPT
commit. Its final 40-case pair reports 16 axis failures becoming passes with
existing outcomes unchanged. Separate recreation-opacity failures were not fixed;
the existing expected vertical-view failure remains a separate timing-sensitive
control. Those historical receipts are not inputs to this proof replay.

Producer closure success is followed by independent formal/native-bridge review
and root replay. This artifact does not mark those independent gates complete.

## Final diagnostic coverage

Every output row retains `raw_axis_style` before inactive-field normalization. The semantic snapshot uses -1 for inactive axis/style; the separate raw pair retains native default enum values. Both views are compared against the independent models. Explicit provided-null, nearest-root-subject and initially empty nearest-parent-chain sequences supplement the source-selection corpus. The nearest product cases fix the subject and pseudo request, so some parameter combinations are duplicate inputs; boundary cases cover pseudo nearest requests independently.
