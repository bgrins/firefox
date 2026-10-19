# Native, model and provider boundary

## Compiled native closure

`generate_native.py` retains whole source definitions/macros/declared data sections for the original55 extraction records. These include the actual ICU trie/category machinery, both text flagging loops, compressed glyph/detail storage accessors, `EnsureComplexGlyph`, font-run iterator and search, ligature counts/widths, spacing helpers, boundary shrinker and both ordinary emphasis draw functions. The complete functions execute in the harness. Extraction records contain source paths and whole-body hashes.

One additional record is explicitly an **arithmetic slice** from the same complete `ComputeLigatureData` definition. It allows counts through UINT32_MAX without pretending to allocate billion-unit buffers. The full consumer path remains compiled and separately exercised. The supplemental slice returns actual part advance/width and clipping flags; it is not counted as another complete consumer.

PUA classification selects `original/layout/generic/nsTextFrame.cpp` or `candidate/layout/generic/nsTextFrame.cpp`. Arithmetic selects the original retained `gfxTextRun.cpp` or the exact separate signed candidate. The replay verifies the complete candidate file equals the original after only the approved quotient/product replacements. Newer live `nsTextFrame.cpp` changes are not imported into this extraction.

## Universal model chain

| Layer | Native-shaped definition | Independent reference / result |
| --- | --- | --- |
| Categories | coarse classification branch | detailed category/exclusion semantics |
| Text | UTF-16 pair/flag loop | direct decoded token flags; Latin-1 theorem |
| Raw storage | bit-mask suppression and detail synthesis | typed glyph suppression, preserved unrelated contents |
| Original admission | raw record count/advance checks, text length, shape and pair partition | post-flag shape and metric validity derived by preservation |
| Font runs | binary predecessor search and complete iterator control | linear last predecessor and clipped interval traversal |
| Boundaries | explicit increment/decrement loops | nearest retained start/end boundaries via list search |
| Ligatures | raw scan of widths and cluster counters | indexed filter lengths and independent sums |
| Font emission | one imperative unit loop with pending eligibility and midpoint state | raw cluster segmentation, eligibility fold and prefix-sum positions |
| Whole run | leading partial, spacing acquisition, font draw, trailing partial, repeated runs | same provider interface with independently derived raw segmentation/geometry |

The top result contains final abstract coordinate, ordered doubled draw positions, absolute end-unit identities and provider/draw trace. The final local coordinate is part of the mathematical state contract; the actual `gfxTextRun::DrawEmphasisMarks` takes its point by value, so the finite external observation is draw positions/identities and provider trace, not an invented getter for that final local value.

## Admitted inputs

`TextInput.Admitted` checks original record/text length, word/detail-count agreement, detailed ID/advance bounds, contiguous font runs, cluster/ligature boundary relations, request bounds, zero spacing inside ligatures, and surrogate-pair continuation boundaries. Empty, singleton and paired inputs are kernel-witnessed; every finite case also has an original-input admission theorem. No final shape, final cache or expected draw list is assumed.

`TextInput.setup_domain`, `setup_surrogate_partition` and `setup_metric_safety` derive preservation after classification. Font order, initial offset and final text endpoint follow from the supplied contiguous partition. Selected clips and shrunk ranges have explicit bounds theorems. `Ligature.raw_denominator_positive`, scan count bounds and `NativeDomain.scanned_arithmetic_domain` connect actual raw scans to safe apportionment.

Shaping still supplies a valid partition and glyph records. This artifact does not prove HarfBuzz, font sanitization, shaping correctness, font loading or the association of arbitrary text with arbitrary glyph IDs. The ordinary path excludes combined-upright alternate drawing. Source-only surrounding functions and root WPTs expose those boundaries.

## Providers

- Classification answers come from actual compiled ICU tables and are independently compared with official Unicode17 data, including recursive NFKD punctuation exceptions. They are not an expected-answer callback.
- Detail allocation/ownership adapters construct valid immutable records and support the actual simple-to-complex conversion. Infallible allocation/OOM termination is outside the successful execution contract; spacing allocation failure is represented and exercised.
- Spacing success is a pure function of requested interval, allocation failure a function of requested count, and letter spacing a raw numeric input. The model admits arbitrary such outcome functions. Finite adapter cases exercise present/absent, enabled/disabled, success/failure and allocation branches; no expected positions are provider inputs.
- Draw targets and downstream mark rendering are observers. The actual native call site records its unit index. Rasterization, clipping correctness, transforms, restyle/cache scheduling and combined-upright behavior remain external.

## Numeric boundary

Signed raw advances remain `Int`; there is no negative `toNat` clamp on the new path. The historical old `ordinaryPlan` is retained only for nonnegative controls. `WidthPolicy.legacyUnsigned32` explicitly models conversion modulo2^32, uint32 division/products and the final signed/double remainder. `WidthPolicy.signed` uses truncation toward zero.

The separate signed contract proves product magnitude at most the absolute int32 width for every selected/index count bounded by the positive total, signed64 safety, the binary64 exact-integer magnitude domain, signed remainder/partition conservation, and unchanged nonnegative legacy results. Actual counters are connected to these premises. This is not a universal C++ compiler or IEEE proof.

`numeric-types/` pins the actual aliases (`gfxFloat=double`, `Point`/`Float=float`, `nscoord=int32_t`) and the harness checks their ABI/precision properties. `metricInputsSafe` names signed intermediate accumulation requirements. `numeric_domain.py` checks a conservative raw-input bound for the finite corpus: integer/half-integer operations remain in a binary32-exact domain. It does not assume final geometry. Legacy negative cases outside that domain are compared with an explicit binary32 reference and retain their rational/float discrepancies as diagnostics. They do not falsely refine signed geometry.

## Source-only and rendered evidence

The original17 complete surrounding style/update/text/run/provider definitions remain source-only. A separate9 complete HarfBuzz/measurement/partial-draw consumers are retained for the negative repair review. Neither inventory is described as compiled full rendering refinement. The root-owned WPT gates and their exact source/binary receipt identities supply rendered/dynamic evidence; this replay only authenticates and rederives those recorded results.
