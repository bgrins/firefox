# Proposed constructor-origin component — approval requested

Status: scope proposal only; no Lean/native model implementation yet. Target the confirmed constructor mismatch, not an additional URL policy theorem.

## Universal core

Use a recursive, finite component syntax with literal UTF-8 fragments, whitespace/comment tokens, ordinary nested blocks, and substitution references containing optional fallback components. Construct source bytes by concatenation. Derive absolute token/reference/fallback positions from prefix byte lengths in an independent layout definition; do not admit desired stored-relative bounds as input.

A source-shaped collector saves one origin, records relative starts/ends while recursively traversing the layout, and builds the stored value. Prove that consuming the initial maximal CSS whitespace token before saving the origin gives the same reference slices as the independent syntax layout after prefix removal, for arbitrary nesting and arbitrary initial absolute parser position. Prove ordered bounds and UTF-8 boundaries for every reference/fallback, including fallback's nonzero start and inferred end. Comments remain part of the stored prefix; VT/NBSP remain content. Prove the legacy trim-after-recording transformation has a concrete failing witness.

Represent EOF closure repair explicitly as a separate provider interface: appended delimiter bytes and at most the already-established terminal quoted-backslash deletion. Show that prefix-origin normalization commutes with any admitted repair satisfying the preceding endpoint/containment contract, and clearly state that this does not independently verify the earlier quote/closure repairs. Do not assume arbitrary repaired endpoints are correct merely because they fit. If authenticating/importing the existing endpoint component cannot establish the required contract, preserve that named conditional premise and report it before claiming complete parser correctness.

Compose the constructor-relative ranges with a source-shaped chunk traversal: monotone cur_pos, legal UTF-8 source slicing, rebased output prefix/inserted separators, and taint ranges measured in serialized output bytes. Reference substitution supplies arbitrary valid UTF-8 replacement strings and an independent provenance bit. Show ranges stay in bounds and each nonempty tainted replacement is covered. Empty tainted strings retain aggregate provenance; no false claim that an empty interval overlaps a URL. This is constructor/range safety, not complete CSS value grammar or security noninterference.

## Native bridge

Retain complete original/candidate VariableValue::parse, parse_declaration_value and parse_declaration_value_block, plus the actual full cssparser crate and complete relevant offset/serialization providers. A bounded source-only harness should expose raw stored text, nested reference/fallback spans and sampled substitution slices for both variants. Require real cases for whitespace, comments, UTF-8, fallback nesting, EOF repair, nonzero initial offsets, invalid VT/NBSP, empty values and observer/cache controls. Native equality/namespace/registration/attribute lookup adapters remain explicit.

Compile genuine semantic mutations: normalize too late/omit it; discard first non-whitespace token by omitting reset; normalize with comment-skipping instead of the exact whitespace-only operation (observable retained text witness); wrong byte/character offset on UTF-8. Pair these with kernel counterexamples of the corresponding modeled contracts. Full compiler correctness and byte-to-token semantic translation remain admitted; finite extraction agreement is not a universal native proof.

## Scope gate

Root must review this architecture before implementation. The common-coordinate theorem is the core required result. A tiny theorem over already-valid arbitrary offsets would leave the constructor obligation open and is not a substitute. The complete quote/EOF parser, general cache epochs, URL loader policy, registration mutation and all CSS grammars are not being silently promised.
