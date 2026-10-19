# Keyframe shorthand conflict ordering

This companion records the specification model and extracted-source checks for the physical-before-logical tie in `compare_property_priority`. It is intended to precede the separate native repair and WPT commit.

## Specification and discovery

The [Web Animations computed-keyframe algorithm](https://drafts.csswg.org/web-animations-1/#calculating-computed-keyframes), retrieved on 2026-10-18 (editor's draft dated 2026-10-08), resolves collisions in this order: longhand over shorthand; fewer shorthand components; physical over logical; then ascending IDL name for tied shorthands. `webspec-index` was unavailable, so the current primary document was read directly. The native implementation had omitted the third comparison between equal-sized shorthands. This was discovered through static specification/implementation comparison and reproduced in browsers before this model was written. The Lean code did not discover the defect.

## Proven statements

`Priority.lean` has 14 audited declarations. `specLE` is an ordered disjunction of the specification's conflict rules. `nativeLE` models the category comparison and shorthand comparison sequence. Their equivalence holds for arbitrary natural-number component counts and IDL ranks. The native relation is reflexive, total, and transitive.

For arbitrary finite declaration lists and arbitrary target sets, `sorted_first_wins` proves that the first declaration targeting a physical property wins the independent pairwise specification relation. `permutation_refinement` transports this result back to the original keyframe. The hypotheses require that the sorted list is a permutation and is pairwise ordered by the modeled comparator. The model does not prove Rust's sorting implementation. `first_none` proves that an absent result means no declaration targets that property. `value_refinement` additionally requires agreement of the values of all winning declarations; it does not prove that native expansion or alias handling establishes this premise.

`uniform_filter` is generic over member identities, a mapping-class predicate, and an independent per-member enablement predicate. Every nonempty filtered subset of a uniformly logical or uniformly physical shorthand keeps the same classification. Empty expansions have no targets and cannot win. The mixed `all` shorthand is outside this theorem. Source review establishes ordinary physical members in `all`, but this package does not formally certify its runtime classification or count dominance under every preference state.

The Lean model excludes the custom-property prepass. It models effective successful expansions supplied by the caller, not parsing, writing-mode conversion, computed-value validity, animation types, or target generation. IDL rank/codepoint correspondence is a finite source check below, not a general Unicode proof.

## Extracted-source bridge

`SOURCE-v1.json` binds nine reviewed fragments to their complete originating file hashes: before/after comparator, iterator/filtering implementation, property-generator fragments, keyframe sorting/first-seen integration, and generated longhand/shorthand/bitset/IDL data. The snapshots permit replay without retaining a build output. `--live` additionally compares those excerpts with current source files, except the historical before fragment. The before source is retained as provenance; the candidate is compiled and checked.

`bridge.py` independently parses all 431 longhand and 95 shorthand entries, checks complete contiguous enum numbering, complete component-map coverage, component identities, the logical bitset, and the full IDL permutation against a separately implemented CSS-to-IDL codepoint ordering. There are 26 uniformly logical shorthands, no empty raw maps, and one mixed map (`all`, 406 components).

The Rust harness compiles the exact candidate comparator and category implementation against adapters for the property representations. It compares all **277,729 ordered pairs of 527 adapters** (431 longhands, 95 shorthands, one custom placeholder) with a separately structured reference comparator. The adapters use **unfiltered generated component arrays**. This is bounded differential evidence for the extracted comparator, not an execution of native `PropertyId`, runtime enablement, aliases, or every preference configuration. The property generator, bitset representation, parsing, and compiler semantics remain trusted/manual boundaries. The separate full Firefox build and WPT gate cover integration.

## Replay and controls

Run from the repository root with the pinned local Lean and Rust compilers available:

```
python3 artifacts/css-logical-shorthand-proof-v1/check.py /tmp/logical-priority-replay
python3 artifacts/css-logical-shorthand-proof-v1/check.py /tmp/logical-priority-live --live
```

The output directory must not exist. The checker authenticates source snapshots and compiler hashes, builds the model in an isolated `LEAN_PATH`, checks the exact axiom audit output, compiles semantic mutations, executes the Rust harness and its mutations, and verifies that all recorded inputs remain unchanged. Successful runs write `PROOF-v1.json` with commands and actual exit statuses.

Controls comprise six Lean mutations (mapping before count, missing mapping tie, reversed IDL/count, discarded matches, wrong targets), five compiled Rust mutations (the four comparator mistakes plus reversed mapping order), nine rejected diagnostic corruptions, nine rejected source corruptions, and four invalid-inventory checks. Lean negatives must fail in the expected theorem bodies with the exact reviewed diagnostic inventory. Rust negatives must compile successfully and then fail at the expected ordered pair. The trusted Lean axiom set is recorded in `expected-axioms.txt`; no admitted theorem or `native_decide` is used.

`tooling-paths-v1.txt` lists source-only companion files. Generated binaries, proof outputs, development logs, and browser artifacts are intentionally not companion inputs. Failed development iterations remain in this directory: initial Lean identifier/instance errors; a diagnostic-span bug; a reused output-directory name; and corrected expected negative-control diagnostics/pair direction. None of those failed runs is reported as accepted.
