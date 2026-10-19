# Independent review: root rlh zoom formal companion

## Decision

**CORRECTIONS_REQUIRED for completion of the approved scope.** The conditional H2 length, provider-selection, cache-publication and finite-trace results are accepted as described below. One explicit promised theorem family is missing: universal dependency-flag preservation. The 1,724 native preservation controls are useful evidence but cannot replace that theorem. Root confirmed that a producer supplement is required; no scope reduction was approved.

This review is of the frozen producer capsule `css-root-rlh-zoom-proof-v1`, not an independent browser or full Gecko build. No production source, WPT, browser/build state or Git state was changed.

| Producer identity | SHA256 |
| --- | --- |
| FREEZE.json | `fc1df491b9bdeafc1781b166752b61b7e6aa090a3aee563673edb8a41812ac13` |
| SOURCE-MANIFEST.json | `b58c6e38b93dff1cb87ee235d39448c6eeb611ed4ff80e567fb0dc89a1f38750` |
| REPORT.md | `4e444e6f99af1b418ae3cf6812d61e1f0fac4d9e91bac1309de8fa800d70a967` |
| Approved SCOPE.md | `77ea404c5c870f463858a5dae460cde4ddf5b039816d624b6c80f414dbeaf2c3` |
| Original specified/length.rs | `0467c54a65866b4566d4b34d72dff1a29cc87ed2506820dfdc5ca0e57845d7e7` |
| Final v2 specified/length.rs | `aa1e6d7cbac46a713a58646b3c57374c007acd640c187c1b0aa0fce5dfef2302` |

The retained source comparison admits exactly the root-only guard around the former unconditional zoom. The parent patch and WPT identities are `fadf1f0641c541279a47e388090e52455c2c62191dd0eb950677e1e9c741f4c6` and `b03a12394ebecee5c772ec1c655a78f303950825ce3828bc787bfa7e29a0c872`. Browser outcome and standalone application receipts remain parent-owned gates: this review authenticates their retained identities, not their complete historical raw resource closure.

## Required correction: dependency observables

Approved SCOPE.md §5 item 5 promises non-root original/candidate preservation including flags. `Model.lean`'s `Observation` contains source, scaled/exposed lengths, coefficient and `cacheUsed`; it contains no computed-value dependency flags or rule-cache conditions. `nonroot_preservation` therefore cannot state their preservation. `Trace.lean` carries only the cache-usage boolean in addition to the root/cache state. The omission is not remedied by `Grid.lean` or the executable Lean runner.

The complete native selector and builder do retain these effects, and the producer oracle checks their bounded raw values. The required supplement should connect them to the model rather than append an unrelated abstract equality.

### Exact source mapping

| Observable | Retained native operation | Required modeling boundary |
| --- | --- | --- |
| `USES_FONT_OR_WM_RELATIVE_UNITS` | `NoCalcLength::reference_font_size_and_length` calls `builder.add_flags` before base resolution and unit dispatch | Union this symbolic flag into incoming builder flags on the admitted selector path |
| `DEPENDS_ON_SELF_FONT_METRICS` / `DEPENDS_ON_INHERITED_FONT_METRICS` | `StyleBuilder::calc_line_height` selects the flag with current/inherited font; adds it when selected line-height is `Normal` | Root/direct provider selection must preserve the selected flag and pre-existing flags; non-root media/default bypasses the builder helper; descendant/cache does not call it |
| Rule-cache font-size and line-height dependency records | `set_font_size_dependency` in the Em arm and `set_line_height_dependency` in the Lh arm | The Rlh arm changes neither record. State this explicitly for arbitrary admitted incoming records; preserve any control-unit effects included in an expanded theorem |
| `used_root_line_height` | `Device::root_line_height` sets its atomic boolean | Already modeled as `cacheUsed`/trace `used`; keep it distinct from the flags and conditions above |

Native facade constants 1, 2 and 4 encode these three symbolic flag names. They are adapter encodings, not an assertion about Gecko's generated numeric bit positions. The supplement must document that mapping and compare observations accordingly.

### Required statements and evidence

1. Extend the observable/state contract with incoming and outgoing flags, and the relevant rule-cache dependency state. Define native-style effect operations from the actual selector/builder dispatch. For every admitted non-root Rlh world and incoming state, prove original and candidate equality of the complete observable result, including flags and dependency records. The stronger all-role flag-equality result is small and useful, but does not replace the requested non-root length/effect composition.
2. Prove the intended effect contract as well as equality: Rlh adds the font-relative-use flag, adds a normal-provider flag only on the appropriate direct builder path, and leaves the Rlh rule-cache records unchanged. Otherwise two equally incorrect constant flag models would satisfy preservation trivially. A representation as symbolic sets or named booleans is adequate if its bridge to native traces is explicit.
3. Add admitted witnesses with nonempty incoming flags and nonempty dependency records. Include current/inherited normal provider cases for source selection, ordinary absolute/numeric controls, and non-root media/cache cases. Current native fixtures reset builder flags to zero and construct empty conditions; those fixtures do not establish preservation of prior state. Keep real metric production external and normal native cases diagnostic as already declared.
4. Compile and execute at least one actual source-operation flag mutation, such as dropping `USES_FONT_OR_WM_RELATIVE_UNITS`, and a matched Lean mutation. Demonstrate changed dependency observations despite identical length results. A selected-normal-flag mutation or an incoming-state-clearing mutation is also a useful control for the expanded contract. Admission/reference must remain unchanged; an ignored numeric-only mutation witness is insufficient.
5. Extend raw/native/Lean comparisons, complete source-only closure, theorem axiom audit and frozen report to cover these observables. Preserve the final v2 candidate identity and all accepted length/cache evidence. The supplement may be separate, but its source/model/observation mapping must be joined to this capsule explicitly.

This is a proof-scope omission, not a newly demonstrated native flag defect.

## Accepted mathematical findings

I read all seven authored Lean modules, not just the producer report or replay output.

`reference` selects semantic providers independently of stored lengths; `implementation` selects stored current/inherited/default/cache values. The inherited transport hypothesis states that parent effective zoom times the inheritance adjustment equals consumer effective zoom. `inherited_transport` substitutes provider validity and reassociates multiplication; `candidate_refines_reference` then covers all six role/base combinations. The reference does not call the implementation or consume native expected output.

Owner-indexed length/zoom wrappers and nominal document/element/version types retain source identity independently of numerical equality. `Valid` additionally checks document agreement and that root-role consumers identify the selected root. These are model premises, not claims that Gecko validates ghost owner tags. Provider font values are rational fields inside an owner-indexed provider; this is not a separate proof of font-size production.

`original` restores the extra root multiplication. `root_lh_rlh` equates the direct ordinary root paths, while `nonroot_preservation` proves equality of the modeled non-root observation. `coefficient_exposure` and `ordinary_exposed` correctly cancel positive nonzero zoom and preserve the dimensionless coefficient. These statements concern the existing observation fields; their acceptance does not supply the missing flags.

### Publication and arbitrary finite traces

`RootRecord.ready` requires an already valid authoritative provider. `publishNative` unzooms its stored value; `publication_value` derives agreement with the independent semantic root value. Commit invalidates the publication schedule while retaining old cache bytes. The invariant requires cache owner and value agreement only when publication is marked current.

`Request.structural` uses a canonical semantic cache to express provider/ownership conditions; the read theorem does not substitute that value into the implementation. Descendant `valid_actual` derives the real cache agreement from the state invariant and the scheduled-publication premise. Direct and media reads use an explicit cache-independence lemma and remain allowed before publication. Root inherited-base requests intentionally use the parent's line-height semantics rather than asserting equality with the root's final ordinary provider.

`finite_sequence_refinement` is genuine induction over an arbitrary list of events. It combines step refinement and invariant preservation, with admission evaluated on the reference schedule. Read requests can vary consumer zoom, coefficient and providers. Root updates can change identity/version/provider. `foreignUpdate` is modeled as noninterfering by construction and admitted only for another document: correct as an explicit boundary, not a proof of Gecko's device routing.

The stale-refresh mutation preserves a publication event while omitting its store. My independent `ReviewChallenges.lean` constructs publication of 20, an authoritative change to 24, and that omitted refresh. The subsequent descendant request is still admitted; its exposed result is 10 instead of 12 with coefficient 1/2. The cache invariant fails. Thus schedule admission does not circularly require the mutant cache to contain the desired answer. The same file kernel-checks an original root counterexample and a direct read before any publication.

All 66 producer theorems and five independent challenge theorems compile with only `propext`, `Classical.choice` and `Quot.sound` in their printed axiom dependencies. No authored `sorry`, extra axiom or `native_decide` is used. Three failed initial challenge elaboration attempts are retained; they concerned simplifying opaque rational operations in the reviewer-authored challenges, not failures in the producer proofs. Final `challenge.log` contains five successful axiom reports and no errors.

## Numeric admission: accepted interpretation and limits

`ExactGrid` restricts app units to nonnegative integers at most 1,048,576 and requires pixels times 60 to equal that integer. `quantize_grid` proves rational nearest-grid quantization and `appunit_roundtrip` proves its inverse. `ExactProvider` combines semantic scaling and that grid to derive `Provider.Valid`; `exact_grid_world_refinement` supplies those providers to the selector theorem. `ExactRead` relates an exact coefficient product and exposure.

The binary32 record describes a bounded dyadic representation; it is not an IEEE754 machine semantics. In particular, the kernel does not execute C++ rounding, floating multiplication, or Rust compiler semantics. The native interpretation also relies on exact intermediate arithmetic. `domain.py` checks the generated operands/products, scaled font size, app-unit multiplication and addition of 1/2, inverse transport, coefficient product and exposure. My separate checker independently rederives those checks and validates every retained witness's significand/exponent identity and actual binary32 representation.

The selected small bound avoids integer conversion and app-unit saturation, and the ordinary admitted inputs are exact after each relevant native operation. Percentage preparation calls the actual `resolve_line_height_length` with an Em coefficient and creates a Length provider; it does not pretend percentages are native Number providers. The machine-order diagnostic oracle remains separate from rational admission.

**Accepted:** universal rational/model refinement under provider contracts, rational exact-grid provider results, and bounded native agreement on the admitted generated inputs. **Not established:** universal Rust/C++ or IEEE754 correctness, all finite floating values, real-font metric production, arbitrary minimum-font/text-zoom settings, or scheduling readiness. `Binary32Exact` and finite test witnesses must not be described as a verified floating-point implementation.

## Native extraction and caller audit

The source ledger retains 38 complete compiled units and five complete uncompiled caller/predicate boundaries. I checked their bodies against whole pinned source snapshots and read the emitted raw extraction and adapters.

The selected path is complete from `NoCalcLength::to_computed_value_with_base_size` through the full font-relative selector and coefficient/finite normalization. Current/inherited selection uses actual `FontBaseSize::resolve` and builder `calc_line_height`. Device resolution calls the extracted `Gecko_CalcLineHeight`, `ReflowInput::CalcLineHeight`, `ComputeLineHeight` and `GetNormalLineHeight`; actual C++ CSS-pixel/app-unit rounding then actual Rust app-unit-to-f32 conversion execute. Rust resolved-value and C++ computed-style unzoom independently expose the result.

The root publication block really calculates the root provider then unzooms and stores it, and the device getter/setter really operate on atomic f32 bits. The enclosing `finish_restyle` and `line_height_likely_changed` are retained, not compiled or proved. Root admission, provider readiness, change detection and publication-before-descendant-read remain external. H1's not-yet-normalized inherited line-height is deliberately excluded by provider validity; this companion does not repair or verify it.

The ordinary length caller supplies current/current bases; font-size supplies inherited/inherited; the complete line-height resolver supplies current-font/inherited-line-height. The percentage dispatch is retained in its complete caller. The outer cascade/parser/calc path is not compiled into the capsule. This is the approved caller boundary, not a replacement of the selected numeric provider with an expected answer.

The C++/Rust facades are a checked private ABI: matching sizes, alignment, offsets and tags, not Gecko's generated binding layout. Font metrics are deterministic adapters; text inflation is 1, element is null, writing mode is horizontal, computed and used font size agree. The full form-control/normal/fallback branches remain in the extracted source, while the declared adapter inputs bound what is executed. Locking is a no-op in a single-thread test. Ghost versions and document tags are not native cache fields. Unused Au constructors compile; container/viewport/character-width adapters reject out-of-domain calls.

## Independent replay, oracle and mutations

Two fresh replays completed: one from the full copied capsule and one from a relocated source-only closure containing 85 source inputs plus manifests. Both reproduced semantic digest `b4f4eadb91c3c9c73c13b48bd591c2341bb48faac8d96a24352b34bf7c23901c`. Raw compiler commands, output, Lean axioms and traces are retained in `replay/` and `source-only-replay/`.

| Check | Independent result |
| --- | ---: |
| Native variants compiled/executed | 12 |
| Events per variant | 1,934 |
| Reads per variant | 1,874 |
| Admitted exact reads per variant | 789 |
| Separately rederived native/Lean comparisons | 9,468 |
| Original/candidate complete preserved controls | 1,724 |
| Producer role/base/form witness executions | 24 |
| Producer structural/freshness rejection examples | 6 |
| Producer numeric rejection examples | 5 |
| Independent kernel challenge theorems | 5 |

`independent_audit.py` imports no producer helper. It walks authored events with its own rational provider/publication/consumer calculation, decodes actual native f32 bits, checks selected owner, cache and usage, and compares every admitted Lean row. It does not take semantic answers from producer RESULT.json. It also independently validates the extraction source/body identities and all complete preservation controls. This supplementary executable audit is not a proof of the implementation language semantics.

| Variant | Independently reproduced value differences |
| --- | ---: |
| Original / restored extra root zoom | 104 / 104 |
| Dropped cache zoom | 393 |
| Scaled publication | 389 |
| Default root provider | 138 |
| Wrong inherited base | 64 |
| Wrong document provider | 521 |
| Stale admitted refresh | 393 |
| Dropped coefficient | 584 |
| Duplicated coefficient | 584 |
| Dropped inherited transport | 52 |
| Candidate | 0 |

All mutants compile and produce semantic witnesses. Wrong-device and stale-refresh variants deliberately mutate bridge/provider behavior; the report labels them accordingly. Coefficient mutations leave percentage input preparation untouched. The original and explicit extra-root-zoom mutation agree in admitted results. These are existing numeric/source/cache mutants, not coverage of the missing dependency-flag theorem.

The separate machine-order oracle reproduces every archived raw event/operation trace during both replays. I reviewed that oracle against the extraction and input protocol, including inherited font-size tracing, percentage preparation, persistent context state, foreign-cache usage and synthetic root+media precedence. Independent arithmetic here targets the exact 789-read partition; the remaining diagnostic trace comparison is producer-oracle replay plus code review, not a second independently implemented full machine oracle.

The 24 role/base/form samples enumerate the current-provider form input. They do not mean every selected default/parent provider receives all four forms in every native case. Ordinary media fixtures use absolute initial line-height and zoom 1; normal-provider native cases are diagnostic. This coverage wording should remain precise.

## Normative connection

Current [CSS Values font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths) gives ordinary root rlh the root lh basis, routes self-referential font/line-height uses to parent or initial metrics, and uses initial metrics outside an element context. The model's role/base split reflects these distinctions with caller readiness supplied externally. It does not define actual line-box height or font matching.

[CSS Viewport zoom](https://drafts.csswg.org/css-viewport/#zoom-property) composes effective zoom through ancestors; its [CSSOM interaction](https://drafts.csswg.org/css-viewport/#zoom-om) exposes non-auto/non-percentage computed-style lengths unscaled. This supports the model's single physical scaling followed by exposure, without imposing a particular internal storage stage on Gecko. Fresh primary snapshots and retrieval identities are retained under `spec/`.

## Closure and trust audit

`verify.py` authenticates frozen manifests and all selected local inputs before importing a custom helper. The source-only replay uses a newly created output directory, an explicit capsule working directory and a fresh Lean import path. Python custom imports and Lean imports are inventoried in `CLOSURE-AUDIT.json`; source extraction reads retained files only. No live Gecko source/build or archived generated result is needed for source-only replay.

The toolchain checker authenticates the Lean executable and 10,183 retained dependency pins before invoking Lean. Compiler entry hashes/version output, Python version and architecture are constrained. The Python runtime/stdlib, system SDK/libraries, OS and actual compiler installation behind rustup remain trusted external infrastructure. This is source closure plus toolchain identification, not a verified compiler or OS.

Independent tampering of the model, helper and source fails authentication before any replay directory is created. An additional undeclared input is also rejected. All four results, including raw stderr and exact commands, are retained in `TAMPER-RESULTS.json`; the helper's injected execution marker never runs. The tamper workspace was restored to its source-only bytes afterward.

Run `python3 -I -S check.py --expected-freeze DIGEST --recheck` in this directory to authenticate the complete independent artifact before importing its arithmetic checker. The root-level MANIFEST and FREEZE are the only self-describing exclusions; nested producer manifests, all replay outputs, specs and failed reviewer challenge logs are included.

## Handoff

Keep the accepted H2 units/cache/native evidence. Obtain the producer dependency-observable supplement, review its universal statements and source mapping, then rerun/freeze the joined closure. Do not mark the full approved formal milestone complete before that correction. Parent native/WPT/standalone acceptance remains a separate gate.
