# Public declaration storage operations

Status: active work, not an accepted or frozen component.

Prove native-shaped parser-priority push/extend and removal/clear preserve the
separate declaration, importance and membership representation. Compare parsing
against an independent forward setter that rejects normal declarations replacing
important ones and otherwise moves the replaced identity to the end. It must not
reuse CSSOM priority-overriding semantics.

Derive deletion indices and the changing loop cursor from the original source
list. Compose arbitrary mixed operation histories after each operation has its
own representation and uniqueness proof. Ordinary batching is a separate active
component and is not assumed complete here.

Bind complete native operations and callers, including preparation-to-mutation
stability. Native value representation, callbacks, machine arithmetic, allocation
and compiler behavior remain explicit admissions. No new defect is established.

## Initial kernel checkpoint

Twenty-six universal lemmas compile and their exact axiom reports use only
standard Lean axioms. They cover parsing priority and unrelated values, scan
validity, insert-before-scan membership, arbitrary sequential extend (including
duplicate source identities), deletion target bounds, removal-loop safety, the
earliest-removal optimization, clear, and arbitrary mixed parse/remove/clear
histories and prefixes. Payloads have no decidable-equality requirement in the
model; classical equality is used only in inherited proof helper applications.

The representation covers declarations, importance bits and membership. The
block's immutable flag and changed-return bits are not modeled. Full CSSOM
setting, callbacks, animation-map constructor coherence and native loop
translation remain outside this checkpoint. In particular, arbitrary public
histories here means exactly the three constructors in Operation, not every
Stylo entry point. Independent static caller review and native interpretation
gates are pending. No new bug is claimed.

Replay: `python3 -I -S replay.py --output /absolute/new/directory`. Source pins
and the exact theorem roster are in CHECKPOINT.json. This active directory is
not a sealed final component; the signed Git checkpoint preserves its version.

## Query and callback checkpoint

Nine additional kernel results in PublicRemoval derive absence and the earliest
matching-index certificate from a forward query, prove queried and cached-index
removal, and transfer the query across a callback preserving ordered property
IDs. The callback may change values or importance provided the resulting storage
is valid; actual callback stability is still a source/provider premise. A
concrete witness shows why deleting an earlier entry invalidates a cached index.
The total current roster is 35 results. Native query/removal correspondence and
its container implementation remain pending; invalid-index branches in the total
model are outside every admitted removal theorem.

The completed static caller audit and animation-map follow-up are in
../css-declaration-public-operations-static-v1/ and
../css-declaration-animation-map-admission-static-v1/. They establish no browser
bug. Animation map key/value identity coherence remains a constructor admission.

## Native query and singleton transfer

Independent review accepted the 35-result checkpoint, retaining its immutable
snapshot in ../css-declaration-public-storage-independent-v1/. PublicAPI adds
nine kernel results addressing two specific source joins from that review:
exact membership justifies the native nonshorthand query shortcut; uniqueness
justifies immediate return after single-property deletion. Shorthand deletion
uses the suffix loop. The joined parse/remove/clear history now uses the queried
API model, and a separate cached callback theorem preserves the same ordered-ID
frame. The complete current audit roster is 44.

The history does not include an intervening callback as an implicit no-op. Actual
callback-aware caller histories still need the stated frame and valid postcallback
storage, and native while-loop/container/machine translation remains open. Native
property-ID membership is interpreted as a fixed predicate here; generated
provider identity and callback stability of that predicate are explicit. These
new joins have root kernel replay but are not included in the earlier independent
35-result review.
