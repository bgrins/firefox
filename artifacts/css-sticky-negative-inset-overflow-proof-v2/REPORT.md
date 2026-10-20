# Negative sticky insets: complete conditional formal/source companion

Status: complete conditional companion, sealed for independent review. Final canonical-v2 and relocated-v2 replays pass with identical results; 22 capsule controls and two resealed-outer cache controls pass. Independent acceptance remains the parent's review decision. This handoff preserves all eight requirements in SCOPE.md.

## Results

- 219 kernel-audited theorem declarations across 19 proof modules: 55 newly written declarations, 12 unchanged preliminary negative-inset results, and 152 inherited library results. The additional Rows module executes references and domains; it is not counted as proof.
- 272 corpus cases per repaired source profile; 544 independently executed Lean rows agree with Python minimum/projection semantics.
- Genuine combined-before/after and standalone-before/after source files replay at O0 with assertions and O2 with NDEBUG, all with UBSan. Each before run admits 269 cases; each after run admits all 272. Total: 2,164 non-mutant native observations. Provider traces are also compared exactly.
- Nine compiled semantic mutants run successfully and disagree with the reference: normalization sign, auto activation, logical end selection, far border sign, parent offset sign, position direction, omitted intersection, wrong continuation, and omitted clamp. They are semantic executions, not compilation failures counted as catches.
- Three false kernel judgments fail compilation. Two separately compiled axiom controls reach the axiom report and are rejected for an unauthorized axiom or sorryAx.
- The existing clamp-overflow frame is rejected by the full caller domain and reproduces the same UBSan subtraction in all eight genuine native configurations. It is not classified as a new regression or claimed repaired.

## Requirement-by-requirement result

| Requirement | Evidence and limitation |
| --- | --- |
| Genuine four source roles | source_roles.py binds exact bytes to original baseline/candidate/standalone test and transfer receipts. Packaging preserves the independent three-file patch. No live source is read. |
| Signed64 normalization and signed32 narrowing | WideNormalization.machine_end_refines checks actual subtraction order, each wide intermediate and result narrowing. provider_bounds_supply_narrowing derives sufficient geometric bounds. storage_type_alone_insufficient rejects the typedef-only argument. |
| Old-defined compatibility and new direct edges | every_old_defined_normalization_unchanged derives the new narrowing from the old admitted result. defined_legacy_edges covers old setter/query temporaries. complete_machine_limits checks the new direct edges and containment arithmetic. Three admitted new cases per profile exceed the old normalization domain; the wide edge witness also rejects forbidden old extent storage. |
| Both coordinates and scroll spaces | complete_position/both_positions join machine normalization and geometry to masked reference movement. Optional projection and closest-feasible lemmas apply to the same reference. both_translation_components bounds both point subtractions. |
| Full absolute range caller | complete_contain_record/complete_contain_join carry the actual machine-computed containment record into FromRect. complete_absolute_caller includes direct stick edges, every side write, checked conversion, Intersect cross-axis zeroing, IsEmpty and all executed MoveInsideAndClamp temporaries. |
| Per-axis callers | complete_axis_caller preserves missing-offset/all-auto early returns, requires both core axes on entry, and models optional thresholds/distances and the ordering-clear branch. DebugSafe records finite-sentinel assertions separately. First-continuation identity is an explicit entry-provider boundary, exercised by native cases and a mutant. |
| Whole extraction and independent semantics | 53 exact source-body bindings per variant, including the actual StickyLimits header record, complete caller bodies and relevant geometry/writing-mode helpers. Native facade providers are visible. Lean reference rows and Python results are independently executed and compared to native outputs. |
| Closed reproducibility and trust controls | Exact source/capsule inventories, source-role gate, full installed Lean bin/lib inventory, compiler identity and separate debug/optimized header lists (965 total headers), axiom roster, canonical replay, manifest-only relocation, integrity controls, and owned-product cleanup receipts. |

The old-defined argument is composed from unchanged geometry expressions, the old/new normalization equality, and the storage-equivalence theorem; it is not a compiler-verified universal theorem about the C++ translation unit. Native calibration verifies the genuine source variants on the finite admitted corpus. Compiled unchanged functions not called by this driver do not expand the claimed proof scope.

## Retained range limitation

The complete clamp frame has x stick edges [0,0], y stick edges [-1073741823,1073740223], containment [0,0,6000,59400] and normal position [0,12000]. Old normalization and the old stored stick height are representable. The empty x interval selects the clamp branch, whose outer y height computes:

`1073801223 - (-1073740223) = 2147541446`

That exceeds signed32. The kernel proves rejection by AbsoluteSafe; both old and repaired extracted native callers report the same overflow at both optimization levels. Browser reachability is not established here. Conversely, the repaired wide case with y far edge 1073747223 is admitted when the clamp branch is not taken; its endpoints are never forced through a signed32 width.

## Admissions and trust

Read capsule/ADMISSIONS.md and capsule/SOURCE-MAP.md together with the theorem statements. Geometry union/transform output, frame graph and identity, percentage/anchor resolution, scheduling, reflow and timeline arithmetic remain explicit provider or out-of-scope boundaries. Local padding Deflate is bounded before the TransformRect output boundary. No universal all-coordinate safety or full CSS conformance is claimed.

The branch-specific domain is a computed expression predicate, not a blanket assumption that the final result is safe. Some core checks are conservatively stronger than a particular caller's executed reads. A caller can fail the domain because of a preexisting overflow or sentinel assertion; that failure is retained rather than silently removed from the contract.

The source-to-model mapping and extraction adapter are human-reviewed trust boundaries backed by finite calibration. Lean's kernel, its approved axioms, pinned tools/headers, Python, OS and dynamic runtime remain trusted. This artifact does not claim C++ compiler verification or replace the existing native/WPT review.

## Reproduction and evidence

`python3 -I -S check.py --manifest-sha <outer FILES.json SHA256> --out <new directory outside this artifact>` authenticates both inventories and reruns the complete capsule. `--verify-only` authenticates without compilation. The exact capsule pin is embedded in check.py.

Canonical and relocated runs retain all compiler commands, generated extraction, inputs, native stdout/diagnostics, independent Lean rows, theorem/axiom logs, mutants and cleanup receipts. controls.py reproduces the source/integrity guards; outer_controls.py checks that resealing an outer inventory cannot admit extra nested caches. Their failed initial harness attempt and subsequent corrected run are retained.

Development failures remain visible: inherited linter warnings initially stopped an overly strict helper; proof-script errors were corrected; the initial compiler invocation lacked the SDK; one initial replay assumed identical debug/optimized header sets; and the first guard runner reused an already-created output directory. These were development/replay-harness failures, not hidden successful evidence or new native defects.

All work is confined to this new artifact. Earlier preliminary/native/review artifacts, production source, WPT, Git, shared documents and Firefox builds remain untouched. Compiler products and disposable relocation/control copies are removed only after retaining their evidence and hashes.

The first canonical/relocated pair used an algebraically equivalent swapped operand order for near-end normalization. Before final handoff this was replaced by the literal native near-then-far machine order, with separate bounds for every near-end intermediate. The successful earlier receipts and exact changed-source preimage are retained; canonical-v2 and relocated-v2 are the final source identity.

The initial outer authentication also rejected an empty dSYM directory left after deleting its owned executable. The remaining owned debug bundles and empty directories were removed; the rejected outer inventories and directory-cleanup receipt are retained.
