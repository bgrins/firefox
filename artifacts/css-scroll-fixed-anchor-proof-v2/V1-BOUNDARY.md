# Fixed-position scroll-anchor selection companion

This artifact binds the local fixed-position exclusion repair to complete extracted candidate/selection/traversal functions, independently modeled frame observations and a Lean structural model. It is **not a proof of all scroll anchoring or native C++ memory safety**.

## Replay

```
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-scroll-fixed-anchor-proof-v1/verify.py
PYTHONDONTWRITEBYTECODE=1 python3 artifacts/css-scroll-fixed-anchor-proof-v1/check.py --out NEW_EMPTY_OUTPUT_DIRECTORY
```

The output directory must not exist. The checker runs original/candidate C++, Lean theorem/axiom auditing, Lean executable comparisons, semantic mutations and separate diagnostics. `--skip-mutations` produces an explicitly incomplete preflight, never accepted preparation. Runtime/source inputs are hashed before and after execution. `SOURCE-ONLY-v1.json` enumerates the portable source capsule; `verify.py --source-only` checks that closure without requiring retained producer binaries/logs. To export that capsule, copy every listed path with its relative directory structure and also copy `SOURCE-ONLY-v1.json` itself; the manifest does not hash itself. Tool executable paths/pins remain environment prerequisites, not bundled toolchains.

## Native boundary

`bridge.py` authenticates each retained source before extracting complete token-balanced bodies. Both original and repaired variants contain:

- `ExamineAnchorCandidate`, `FindAnchorIn`, `FindAnchorInList`;
- `SelectAnchor`, `CanMaintainAnchor`, and `SetAnchorFlags`;
- the exact four-case result enum and both placeholder helper bodies.

The extraction receipt has eight records per variant: six functions, one enum and one bundle containing two helper functions. No production function body is rewritten in ordinary original/candidate generation. Semantic mutations change generated copies only. Assertions remain active. Logging/profiler macros are inert and do not evaluate their diagnostic arguments.

`adapter.cpp` supplies stable owned frames, style observations, ordered child lists, ancestry, rectangles and offsets. All frames have real allocated C++ objects for the duration of a case; vectors owning anchors and objects are allocated before pointers are connected and never resized. The placeholder adapter's casts are valid in this fixture hierarchy. This does not establish the actual Gecko class layout: all fixture nodes share a concrete derived storage type, while query-provider flags describe their intended frame role.

`Frame()` is an explicit owner-pointer adapter. It does not copy Gecko's containing-object pointer arithmetic into an incompatible fake layout. Geometry helpers return supplied rectangles/offsets. This is a declared provider boundary, not exact native geometry extraction. Rectangle intersection is independently mirrored for small integers; general transforms, continuation union geometry, zoom and floating point remain outside the proof.

The public caller, flags and maintenance gates are executed, so the evidence is stronger than a predicate-only certificate. PresShell's retained queue caller establishes the integration path but is not compiled into the fixture. No distinct focused/find-in-page priority selection is implemented by the inspected native path. The model preserves the native list and fallback priorities; it does not claim complete conformance to specification priority candidates.

## Independent semantics and theorem boundary

`fixtures.py` derives classification from independent Boolean observations and geometry inequalities, then interprets ordered graph searches and public selection effects. C++ emits both state and provider/visitation events. The checker compares the complete row, not only the selected ID.

`Anchor.lean` proves fixed/sticky exclusion, selected-node safety, unchanged classification for non-fixed frames, selection and visitation preservation for graphs without fixed observations, the four result branches, and conditional excluded-subtree barriers. Its graph layer models list filtering, absolute second pass and placeholder resolution. A rank premise gives decreasing recursive descent; the unfolding-stability theorem proves sufficiently deep expansions stop changing. Repeated references and the second visit are allowed. A finite unrolling is not silently assumed to match unbounded native recursion: input validation rejects cycles and all fixture graphs use more expansion fuel than their maximum descent depth.

The strongest subtree statement is conditional: a target absent from remaining alternate routes cannot be selected through an excluded occurrence. The corpus intentionally includes an abstract alias graph that bypasses an excluded ancestor. Both the real extracted traversal and the graph model can select that descendant. This is **not a claim that Gecko constructs that graph**, and it prevents falsely concluding universal DOM-subtree exclusion from a local classifier.

Lean public-selection and flag/state lemmas are abstract transition facts. The exact `SelectAnchor`/`SetAnchorFlags` execution plus bounded full-state comparison is separate bridge evidence. The actual browser's physical parents, frame construction, geometry, style values, ownership/lifetimes and stable-provider behavior remain premises. No adjustment arithmetic, suppression endpoint, APZ or scheduling theorem is claimed.

`lean_cases.py` independently resolves raw flags and rectangle observations in Lean, constructs raw node arrays/list kinds/placeholder mappings, and exports original/repaired decisions and examination order. The exported results are checked against the Python oracle for every native case. Source order/classification in the Python oracle is not imported into the Lean model. The graph `within` provider is explicitly derived from supplied physical parents, not a proof of Gecko frame ancestry.

## Corpus and raw schemas

The corpus has 4,929 cases: 4,170 direct complete-classifier inputs and 759 calls through `SelectAnchor`. It covers all five position values, early exclusion combinations, full/partial/disjoint/zero-area geometry, text/continuations, replaced/non-replaced inline distinctions, anonymous boxes, nested scroller boundaries, all six adapter child-list kinds, placeholder ancestry, absolute second visits, ordered fallback, maintenance gates, old/new flags and highlight invalidation calls. This is bounded structural coverage, not enumeration of all valid browser frame trees.

`cases.json` retains complete named input records. The numeric `inputs.txt` schema is:

1. Header: case ID, entry mode (0 public selection; 1 direct candidate examination), frame count, enabled preference, highlight preference, old anchor ID (-1 none).
2. One row per frame: physical parent ID, placeholder target ID, previous continuation ID, position enum (static/relative/absolute/fixed/sticky = 0..4), flags, nested anchor ID, disabled, logical x/y, rectangle x/y/width/height, bounding offset.
3. One list block per frame: list count, then list kind/count/IDs. Kinds principal/absolute/float/overflow-floats/fixed/other = 0..5.

Flag bit indices: text0, native-sticky1, br2, chrome3, pseudo4, replaced5, inline-inside6, anonymous7, scroll-container8, dirty-children9, perspective10, vertical11, absent-content12, overflow-anchor-none13. The synthetic sticky-frame predicate is independent of the position enum to avoid baking an unproven style/frame correspondence into the model.

Native output: `case result offset dirty suboptimal flag0...flagN|events;`. Result is selected frame ID (-1 none) for mode0, or Exclude/PassThrough/Traverse/Accept = 0..3 for mode1. Events: `L` child-list enumeration, `A` absolute-list access, `H` placeholder target access, `P` ancestry result, `E` examination, `Q` scroll-container query, `B` bounding geometry, `F` chain flag update, `I` highlighting invalidation, `O` bounding offset. These are provider observations from verbatim code, not inserted instrumentation inside extracted bodies. They expose visitation and geometry access order; the direct mode separately checks all classifier return alternatives.

Lean output contains case ID, original result, repaired result, original examination IDs, repaired examination IDs. All native/Lean row counts and identities are checked. Semantic mutations must compile, exit zero, emit the full corpus and produce at least one selected-value/state mismatch. Trace-only differences alone do not satisfy a semantic mutation gate.

## Mutations, diagnostics and rejected preparations

Twelve native semantic controls remove fixed/sticky exclusion, overexclude absolute positioning, pass through fixed/sticky subtrees, reject valid local placeholders, examine placeholders instead of their target, omit the second absolute pass, corrupt Traverse/PassThrough/Accept priority, bypass maintenance, or retain obsolete anchor flags. Six Lean mutations independently challenge exclusion, traversal, absolute ordering and the public maintenance gate. Each must both fail the original theorem checks and successfully execute an explicit counterexample using the same changed definitions with all theorem declarations removed. `lean_mutations.py` specifies six ordinary finite witnesses and their independently expected reference/mutated selection and visit outputs. The executable gate requires exit zero and exact distinct outputs; a proof compilation failure alone is not semantic evidence. Removing theorem declarations does not change executable definitions.

Removing placeholder ancestor rejection altogether lets an external target reach the real `SetAnchorFlags` assertion. That exact mutation is retained as a **caller invariant diagnostic** with partial output, not a successful complete-corpus semantic test. The valid-local-placeholder rejection mutation supplies the full-corpus semantic ancestry control. Compiler API rejection, prohibited proof constructs, source drift and malformed graph validation are also diagnostics, not semantic evidence.

- `preflight-v1`: rejected. A first independent oracle incorrectly applied the non-replaced-inline condition to replaced inline nodes; 36 comparisons disagreed. Subsequent local Lean drafts had declaration/proof errors. Those logs are retained and not counted as acceptance.
- `preflight-v2`: passed ordinary native/Lean comparisons but intentionally skipped mutations; incomplete evidence.
- `preparation-v1`: rejected. The runner initially required the removed-ancestry mutant to finish the corpus, but its public caller assertion stopped execution. This led to the explicit diagnostic/semantic split above. No partial row count was credited as a semantic success.
- `preparation-v2`: passed the original full gate but was superseded during root review because Lean mutations only required theorem compilation failure. It does not satisfy the stronger executable-counterexample requirement.
- `preparation-v3`: rejected because Lean emitted an unused-variable linter warning alongside a changed witness result; the exact-output gate rejected it. The theorem-elided executable copies now explicitly disable that linter without suppressing errors. All twelve reference/mutated witness executions then passed a separate preflight.
- Only the final successful full preparation identified in `FINAL-v1.json` is accepted producer evidence. Root replay and independent review remain necessary.

## Tools, browser binding and limitations

`TOOLCHAIN-v1.json` pins actual Lean/compiler executables, compiler realpath and SDK settings; the checker records and matches actual version output. Native runs use UBSan and implicit-integer-truncation sanitization with nonrecovering errors. **No ASan execution is claimed.** Earlier independent tasks found ASan startup unavailable; this capsule does not treat those old attempts as a fresh runtime diagnostic or a memory-safety proof. The SDK headers, compiler support libraries and Lean standard library are not a hermetic vendored distribution.

Retained browser source identities and root reviews bind the companion to fixed-child repair source SHA `6e2b229b29e73f499abd6807c5f9c8ac17451e2e605b335b620082d102bcd00c`, WPT SHA `e47377df7cff6ca5e6247fc8de3b42a22809258218befc282682a196cef19289`, baseline94273 exit1, build17708 exit0, paired41566 exit0 and boundary25742 exit0. The paired gate has five new and three existing PASS cases; the 13-case boundary probe changes only the fixed-transformed failure while retaining the separate scroller-margin failure. These are root browser results, not browser runs performed by this producer.

The intended claim is structural selection safety/preservation under explicit providers, with bounded execution of the exact native classifier/traversal/public caller. It does not certify all CSS Scroll Anchoring, all frame graphs or universal native refinement. Keep this tooling companion separately reviewable before the single native+WPT bugfix commit.
