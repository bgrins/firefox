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
