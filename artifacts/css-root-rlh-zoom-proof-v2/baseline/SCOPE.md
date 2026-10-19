# Proposed scope: root rlh zoom conversion

Status: submitted for root approval; no proof implementation or native extraction yet. H2 only. The implicit inherited-line-height scheduler defect H1 is a separate repair and is not normalized by this model.

## Objective and acceptance statement

Establish that the candidate rlh provider selection preserves each provider's units, selects the correct current/inherited source, and composes with coefficient multiplication, root cache publication/read and CSSOM unzoom. Prove state/trace properties for arbitrary finite admitted publication/read sequences. Bind the theorem and native evidence to the parent's exact original/candidate source snapshots before freezing.

The repaired root/direct path must use the already scaled line-height once. Media/default and descendant/cache paths must receive their required consumer zoom. Preservation covers root Lh controls, non-root Rlh behavior, coefficient application, cache usage marking and other branches retained in the complete native selector. This is not a proof of all CSS, floating-point arithmetic, font matching, traversal readiness or rendering.

## 1. Typed state and independent semantics

Use distinct nominal types for document/root/element identity, versioned zoom owner, unscaled CSS length, scaled builder length, and app-unit result. A zoom owner includes the element identity and the version of its effective zoom; equal numeric zooms do not erase different owners. A cached root length carries document/root identity and the root publication version, while its number is unscaled. Coefficients are dimensionless and remain distinct from zoom.

The world contains a selected document/root, per-owner effective zoom, current and inherited font-provider records, local inheritance zoom, default media font provider, authoritative root style/version, and a device cache/publication record. Role selection is represented by root/direct, non-root media/default or non-root descendant/cache, with an explicit bridge to native context flags. The native branch ordering for a synthetic root+media flag combination is retained as a bounded diagnostic; that combination is outside the ordinary admitted role partition unless caller tracing establishes it as real.

Current-style providers return a line-height in the consumer builder's scaled coordinates. Inherited-style providers return a parent-owned line-height; the builder's actual inheritance adjustment transports it to consumer coordinates. Default media providers are initial-font inputs under the admitted media context. Descendant cache reads select the same document's published root and then scale to the consuming element's effective zoom. Root current/inherited selection and root versus media precedence are independent of the arithmetic result.

The reference algorithm walks these semantic roles and provider records. The implementation model follows native branches/operations. They must be independently defined, with a refinement theorem; no reference function may call the implementation selector or consume its expected result. Provider identity and trace events are observable even when two numeric lengths coincide.

## 2. Numeric domains and provider boundaries

Two theorem layers avoid conflating exact units with machine arithmetic:

- Universal typed selection/publication/trace theorems quantify over admitted provider values and positive rational zooms. They prove owner transport, source independence and state transitions, with explicit zoom/unzoom laws for the selected numeric interpretation.
- An ordinary absolute/numeric exact-grid interpretation discharges those laws for nonnegative bounded dyadic CSS lengths/coefficients/zooms whose intermediate scaled values are finite and exactly representable and whose relevant app-unit conversions land exactly on the grid. It includes the powers-of-two/integral witnesses and nontrivial fractional coefficients. Explicit bounds exclude overflow/saturation and invalid zero zoom. Admissibility is checked independently on generated cases; it must not be merely a list of expected answers.

Absolute and numeric line-height providers are separate constructors. Numeric line-height consumes a typed font-size provider and factor; absolute line-height consumes a stored scaled length. Percentage line-height is first converted to its computed length by its actual caller/provider operation, then follows the absolute branch. Retain that distinction instead of treating percentages as native `StyleLineHeight::Number`.

App-unit conversion, scaled font-size conversion, `Zoom::zoom/unzoom`, CSSPixelLength multiplication/finite normalization and resolved-value conversion will be extracted with their exact source and exercised. A bounded non-grid diagnostic set will compare the actual native rounded operations with an independent machine-order oracle and recorded tolerances/bit patterns; those observations will not enlarge the universal exact-grid theorem into an IEEE754 proof.

Normal line-height and initial media metrics are external font-metric providers with explicit owner/environment identity and positive finite ordinary outputs. The full native normal/fallback branches are retained and tested with declared deterministic metric adapters. This verifies selection/transport under the supplied metric contract, not real-font metrics or font-download invalidation. `Gecko_CalcLineHeight` uses no element and inflation1 for this path; form-control minima and arbitrary font inflation remain outside the admitted H2 provider profile, with branches retained as named boundary controls.

## 3. Publication/read sequences and freshness

Model arbitrary finite sequences of: commit a new authoritative root style/zoom/version; perform the admitted root publication; read root Lh/Rlh with a selected base; read descendant Rlh; read media/default units; change a descendant zoom/style; and inspect CSSOM exposure. Root direct reads need no cache round trip. Independent descendant zoom changes must not alter the cached unscaled root value.

The external freshness premise concerns scheduling: before a descendant cached read after a root commit, the trace must contain publication for that authoritative root version. It does not assume that the implementation cache already equals the desired answer. The proof derives cache value/version/owner agreement after executing the actual publication operation and carries that invariant by induction over the sequence. A stale-refresh mutant must remain admitted by this schedule while omitting/redirecting the implementation store, so it produces a semantic counterexample rather than being excluded by a circular freshness premise.

The initial state has an explicit default/unpublished cache state. Admitted descendant reads require an initial publication; default/media reads can occur earlier. Prove nonvacuity with concrete initial→publish→read and change→publish→read traces, multiple documents/owners, differing parent/current/default fonts, nonunit zoom and nonunit coefficient. Direct-root reads before publication must still select the live builder provider.

Matching/traversal determines whether and when publication is required. The complete source caller and dependency predicate are retained and traced, but full traversal correctness is an external scheduling obligation. The H1 missing-normalization scheduler cannot be discharged by assuming a current-style provider is ready; readiness remains explicit and H1's failing traces are outside this H2 claim, recorded as a separate negative boundary.

## 4. Source-bound native bridge

Plan a source-only mixed Rust/C++ capsule with independently generated inputs and complete original/candidate extraction units. Exact extraction matches are required; adaptations are recorded per unit and never replace an entire provider by its expected numeric answer.

| Unit | Planned treatment |
|---|---|
| `NoCalcLength::reference_font_size_and_length` | Complete Rust function, including nested metric helpers, every unit branch, dependency/usage flags and original/candidate Rlh delta |
| `font_relative_to_computed_value` | Complete coefficient consumer, finite normalization retained |
| `StyleBuilder::calc_line_height` | Complete body from properties.mako.rs, current/inherited font selection, normal metric flags, inheritance zoom |
| `Device::calc_line_height` | Complete Rust body and real-shaped Rust→C++ FFI transport, app-unit return conversion |
| `Gecko_CalcLineHeight` | Complete C++ body; lock ownership is an explicit single-thread adapter boundary |
| `ReflowInput::CalcLineHeight(StyleLineHeight,...)` and `ComputeLineHeight` | Complete C++ bodies; absolute/numeric executed against extracted length/size conversion; normal provider and null-element branches retained |
| `GetNormalLineHeight` | Retained/extracted branch logic with explicit metrics adapter; no font metric correctness claim |
| `Device::root_line_height` / `set_root_line_height` | Complete atomic-bit getter/setter, usage flag and exact stored/read bits; single-thread ordering contract |
| `finish_restyle` root publication call site | Extract the complete root-line-height publication block; retain the complete enclosing function and `line_height_likely_changed` provider. Scheduling predicate/traversal remains named external boundary |
| Zoom, CSSPixelLength, Au and C++ pixel/app-unit helpers | Exact zoom/unzoom, coefficient, finite and conversion operations used by admitted bridge; retain source closure |
| `CSSPixelLength::to_resolved_value` | Complete Rust exposure operation |
| `nsComputedDOMStyle::SetValueToPixels` | Complete relevant overload(s) retained/extracted for the unzoom exposure path, with CSS value sink adapter; real DOM/style flushing external |
| Font/base caller operations | Trace actual `FontBaseSize::resolve`, line-height and font-size self-reference base selection and percentage computation. Extract complete small operations needed by fixtures; any unextracted cascade caller is explicitly listed as an admitted provider boundary |

Other selector unit branches are compiled, with metric/cache inputs supplied by explicit typed adapters and preservation cases; this is not a conformance proof for ex/ch/cap/ic or their root variants. The source extraction ledger identifies complete bodies versus call-site blocks versus external providers. The test harness records source selection, owner/base, metric calls, app units, coefficient, zoom operations, cache get/set/version and usage/dependency flags, internal length and CSSOM exposure. Byte preservation of untouched branches is supplemented by bounded semantic controls.

The full browser CSSOM/layout path is covered by the parent's WPT gate, not replaced by the capsule. Exact final candidate snapshot binding is mandatory; no locally invented patch is accepted as the parent's final candidate.

## 5. Lean theorem families

1. Well-formed role/provider selection: root/direct, media/default and descendant/cache choose the intended owner and base independently of coincident numeric values.
2. Current/inherited provider transport: the inheritance adjustment is applied once to the selected parent provider, while current providers already belong to the consumer.
3. Candidate/reference agreement for admitted Rlh worlds; original counterexample with nonunit root zoom.
4. Root Lh/Rlh unit equivalence for the same ordinary source and coefficient, and current/inherited distinctions for self-reference callers.
5. Non-root preservation: original/candidate equality for cached/default paths, flags, coefficient and exposure under the admitted profile.
6. Publication stores unscaled root units with correct document/root/version identity; getter marks usage without changing values; read-only operations preserve publication state.
7. Coefficient linearity and CSSOM observation in the exact-grid interpretation, with physical scaling distinguished from exposed unscaled length.
8. Arbitrary finite admitted trace refinement and freshness invariant; independence of descendant zoom and unrelated document/provider updates; fresh-final-state equivalence after admitted publication.
9. Nonvacuity witnesses for each role, both bases, absolute/numeric/percentage-computed provider forms, several owners/versions, nonunit coefficients/zooms and a multi-step refresh trace.
10. Explicit rejection/diagnostic lemmas for malformed owner/role/version/domain inputs. These are model admission checks, not invented Gecko runtime validation.

No `sorry`, extra axioms or expected-data-backed theorem definitions. Enumerated cases supplement these theorems; they do not replace universal sequence induction.

## 6. Semantic mutants and independent checks

Each accepted mutant must compile and execute, with a matched native and Lean model variant and a concrete differing result/trace. Build/type errors do not count.

- Restore extra root zoom.
- Remove cached-provider zoom.
- Store scaled root line-height in the cache.
- Select default font for the direct root provider.
- Select current rather than inherited base, or omit inherited transport (separate variants if both are needed to distinguish selection and units).
- Read/publish the wrong document/root/zoom owner while keeping values intentionally distinct.
- Omit the implementation store during an otherwise admitted refresh, producing a stale descendant read.
- Drop or duplicate the dimensionless coefficient as a consumer control.

Native mutations target actual extracted operations where possible. Wrong-owner and stale-refresh variants that necessarily mutate provider adapters are labeled provider/bridge mutations, not source edits to fields Gecko does not have. All mutants use the same admitted inputs as the valid implementation; none obtains its result by altering the reference oracle or suppressing a premise.

The independent oracle is a separate stdlib implementation using exact rational/grid arithmetic and a distinct state algorithm. It consumes raw inputs, not producer expected values or native traces. It checks final values and complete selected-provider/operation traces. Native floating diagnostics use separately stated machine-order checks. Retain raw outputs, tool commands, successful mutant witnesses, nonvacuity outputs and source extraction identities.

## 7. Closure and completion gates

Before helper imports/execution, authenticate the complete source, adapter, model, case, oracle, compiler invocation and proof input closure. Source-only replay must work from a relocated capsule with no live Gecko/build/browser imports. Pin Lean/toolchain identity and separate external toolchain requirements from vendored computational inputs. Negative tests must reject a tampered model/helper/source before execution.

Parent approval of this scope precedes implementation. Completion requires all promised extraction units or an explicitly approved amended boundary; theorems, native/model agreement, all successful semantic mutants, exact candidate binding, fresh full replay, frozen closed manifest and independent review. Parent's original/candidate WPT/build/lint/standalone patch gates and final repair acceptance remain separate. If a promised bridge proves materially larger, report the concrete gap and obtain scope approval before changing the claim.
