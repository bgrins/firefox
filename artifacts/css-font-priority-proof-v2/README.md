# Font matching priority proof companion, v2

This artifact implements the approved DESIGN-A. The frozen B artifact is unchanged. All five A patch files are copied from the root task's formatted candidate snapshots; `DELTA-v1-v2.json` records their final identities after removal of an unused math.h include. The older format receipt is retained as history, not the final header identity. Browser and WPT validation belongs to the root task.

## Claims

`Priority.lean` proves that successive minimum filtering by width, style and weight equals an independently defined lexicographic scan, including the **entire ordered result list**. The theorem holds for every finite list and decidable total coordinate preorder (and therefore total orders), not only a bounded set of descriptors. It implies ordered identity equality, empty/singleton behavior, preservation of all ties, permutation invariance of the selected set, and matching first/last policies.

The separate presentation extension proves the four-coordinate ordering, rank-2 unmatched sentinel, optimistic-pruning soundness and zero as a lower bound. Zero stopping guarantees no strictly better later key; it does **not** claim that later tied identities or face names would have been considered. The actual global caller intentionally stops at its first exact match.

There are 32 general/arithmetic theorems and 11 successful semantic counterexample theorems. The checker audits every theorem's axioms. Only Lean's standard `propext`, `Classical.choice` and `Quot.sound` are allowed; there are no holes, extra axioms, `unsafe`, or `native_decide` uses.

The universal theorem is about coordinate ordering. It is **not** a proof of C++ translation, IEEE arithmetic, complete StyleDistance conformance, or every CSS font-selection policy. B's same-sign interval/italic-positive result remains separately scoped. Normal/negative-oblique behavior, other cross-kind style branches, and synthesis-disabled legacy behavior are compatibility assumptions here.

## Complete native connection

Four independent builds exercise original, B-only, A-only and A+B. Each uses the complete extracted methods, not replacement score-only loops:

| Boundary | Compiled extraction / observation |
| --- | --- |
| Coordinates and fixed point | Complete StyleDistance, WidthDistance, WeightDistance, generated fixed-point types/constants/macros/inlines and FontPropertyRange; exhaustive valid raw roundtrips and actual default-oblique 14 provider |
| Unshared family | WeightStyleWidthDistance, FindAllFontsForStyle, CheckForSimpleFamily, actual SupportsBold |
| Shared family | WSSDistance, FindAllFacesForStyleInternal, outer GTK bitmap filtering, actual AddFaces |
| Three character consumers | FindFontForChar, both SearchAllFontsForChar methods |
| Global fallback | Complete GlobalFontFallback, both zero exits, platform attempt, visibility, async and unavailable-list branches |
| Presentation / normal request | Actual FontPresentation, PrefersColor and IsNormalStyle |

The inherited closure includes the full caller/provider sources for FontFaceImpl descriptor extraction, Servo specified/computed font types, user-font insertion, common/fallback-family call sites and shared-list structures. Their exact bytes and previous static caller discovery are retained. These **external** providers are inspected assumptions rather than compiled Gecko services. The stand-ins supply raw ranges, ordered family inventories, pointers, coverage, maps, creation/readiness, presentation glyphs, visibility and async state. Locks, IPC, profiler/logging and actual font shaping are outside this standalone adapter.

`provider_oracle.py` starts with rational raw descriptor coordinates, performs successive minimum filtering for A, and separately models provider observations and policy. It never uses the corpus's old literal expected selections. `cases.py` removes those inherited fields before execution. Original and B scalar comparisons are explicit compatibility controls, including each float conversion before/after presentation penalties.

Every native row is compared in full: scaled style coordinates, ordered selected identities, caller counters, the public global cmap-count return, and the ordered provider trace. Global internal counters are not falsely presented as exported; the driver reports its separate unused outer accumulator as zero plus the actual cmap return. Name-call evaluation order is checked for the pinned compiler, not claimed for all C++ implementations.

The final corpus has 12,145 cases per variant and 1,262 per GTK variant: 53,628 compared harness rows: 30,204 enter a complete matching consumer or global fallback, 23,412 are helper-only, 4 exercise fixed-point/default providers, and 8 check adapter ABI. The 30,204 entries comprise 26,280 direct five-consumer rows (including construction-plus-matching) and 3,924 global-fallback rows; these are not exact nested function-invocation counts. It includes random raw ranges/provider combinations, boundaries, all simple-family slot subsets, >500 versus >=600 simple-provider thresholds, ties/alias identities, failed maps/fonts, presentation modes, missing glyphs, global zero/mismatch exits, and actual constructor/default providers. The simple paths intentionally retain their existing differing threshold policies; this artifact does not newly certify those policies as CSS conformance.

Unshared general-list output uses reverse traversal and existing adjacent duplicate-pointer suppression. Shared output preserves forward traversal. These native wrappers are distinct from the abstract occurrence-preserving theorem. The oracle explicitly models both. GTK size filtering remains a post-selection policy. Allocation traces check the adapter ABI (`Pointer` 16 bytes, `Face` 48 bytes), not Gecko's production object layout.

## Mutations and numeric boundary

All 11 semantic mutants compile and exit successfully, disagreeing on selected identities with the independent oracle. Each has a corresponding **successful Lean proof and executable evaluation** of expected and mutated outcomes in `Witnesses.lean` plus the generated `Audited.lean`.

| Mutation | Expected → mutated IDs |
| --- | --- |
| Restore weighted addition | `[0]` → `[1]` |
| Swap width/style | `[0]` → `[1]` |
| Swap style/weight | `[0]` → `[1]` |
| Round combined weighted key to float | `[1]` → `[1,0]` |
| Sentinel rank zero | `[0]` → `[]` |
| Drop presentation | `[1]` → `[0]` |
| Ignore mismatch in IsZero | `[1]` → `[0]` |
| Shared strict comparison becomes nonstrict | `[0]` → `[1]` |
| Drop equal-score entries | `[1,0]` → `[1]` |
| Remove clearing on improvement | `[0]` → `[2,0]` |
| Reverse unshared traversal | `[1,0]` → `[0,1]` |

The combined-key witness holds width and style equal and varies one weight quantum. Its exact-double weighted control still selects `[1]`; only float rounding creates the false tie. The Lean witness uses integer scores scaled by 256 and the actual local binary32 quantization interval (8192 in unscaled score units); it is a concrete rounding witness, not a general IEEE formalization.

Narrowing **individual coordinates** to float is not a semantic mutant on the valid domain. Generated fixed-point values are exact; helper distances are multiples of 1/256 below 2000, so their scaled integers fit in fewer than 24 significant bits. The artifact proves the integer bound, exhaustively executes the actual fixed-point providers, checks rational coordinate representability throughout the corpus, and executes the coordinate-float variant against all 12,145 ordinary harness rows (6,290 consumer-entry rows, 5,853 helper-only, one provider and one ABI). It records a no-op, never a fake mutation kill.

Raw provider premises: valid ordered inclusive ranges; weight raw 64..64000 and width raw 0..64000 (10.6); slant raw -23040..23040 (8.8), or the italic singleton 25600. Deserialization of arbitrary malformed values, NaN/infinity, variation-axis application and unmodeled platform provider semantics are excluded. Helper bounds and finite values are asserted in the extracted native code.

## Cost experiment

`benchmark.cpp` calls all five complete consumers with families of 100, 1,000 and 10,000 faces, both varied coordinates and all-tied descriptors. It records checksums and provider-call counts as well as process CPU time and wall time. All variants use the same O2/UBSan compiler flags. Seven samples per case in each of three interleaved variant orders produce 21 samples per median.

This is an instrumented extraction experiment on a shared host, with an external Gecko build potentially active. Provider call counts are useful deterministic evidence; timing differences are observations, not a browser performance guarantee. See `COST-REVIEW.md` and the retained individual samples. The native algorithm remains one scan; the spec oracle's repeated filters are not shipped implementation code.

## Reproduce and authenticate

Run `python3 artifacts/css-font-priority-proof-v2/check.py --out /private/tmp/font-priority-replay`. The checker authenticates its input manifest and every source **before importing any local helper**. It checks the compiler, Lean binary and SDK settings identities. It copies only the authenticated source closure to an isolated directory and compiles all native variants, runs their exact row comparisons, executes native and Lean mutations, and records the cost experiment. No live Gecko source, object files, browser, or prior result receipts are inputs to replay.

`INPUTS-v2.json`, `FREEZE-v2.json` and the final handoff provide content identities. `INHERITED-B-v1.json` independently authenticates every copied B source. `AUTH-NEGATIVE.json` records rejection of altered helper bytes before an injected side effect can run. Native mutation patches are applied only to generated extraction strings. No Git/build/browser work is performed by this companion.

Canonical results are under `receipts/source-only/isolated-results/`. The current Fonts 4 matching section and Searchfox/provider evidence are frozen within `support_b/evidence/`; the specification source is https://drafts.csswg.org/css-fonts-4/#font-style-matching. Root-owned live browser results are deliberately not prerequisites for this mathematical/native artifact and must be assessed separately before landing.

## Refresh boundary

The v1 artifact remains immutable. `refresh.py` checks every complete generated native translation unit and every extracted body against retained v1 bytes/hashes, verifies the header-only include deletion, and checks unchanged Lean/model/provider/driver/corpus inputs. `DELTA-v1-v2.json` and `REFRESH-REVIEW.md` describe the refresh. New source-only success, native/Lean mutation and cost receipts are produced from the final five candidates; browser and lint gates remain root-owned.
