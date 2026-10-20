# Source mapping and explicit admissions

The exact source delta changes only the per-new-entry predicate in `KeyframeEffect::EnsureBaseStyles`. Original SHA `02ffed21d1fbbce1bd58d0df9964fa23cf1d162f3bb74212bf9e4096296463bf`; final formatted candidate SHA `cee5ea606d98c23cd609b9f09f87f97d871530de059ac7e31478c025fe87cc13`. `native.patch` is regenerated from both complete files by the checker. The unformatted proposal was reconstructed from the observed wrap after the proposal directory advanced, then authenticated against root’s earlier external hashes (see UNFORMATTED-RECONSTRUCTION.json); the exact formatter delta is retained: the wrap before `previous.mServo` is the only difference. It is not a change to the `previous(...)` assignment.

| Native operation | Lean counterpart | Remaining admission |
|---|---|---|
| Iterate `mBaseValues` after rebuilding | arbitrary finite `entries : List (K × Endpoint P)` | Every actual new entry appears; stable map traversal and key decoding, no intervening mutation |
| `previousBaseStyles.Get(entry.GetKey())` | `old entry.1` | Same property identity/name in old lookup and new entry; missing lookup and stored null both map to outer `none` |
| `AnimationValue::operator==`, deep equality | `endpointSame cmp` | Nonnull payloads translated to P; comparator matches native result. No reflexivity or comparator soundness required for preservation/decomposition theorems |
| `IsCustom()` | `custom entry.1` | Key classification and native AnimationValue variant agree with the representation |
| `value.mServo && previous.mServo` | both outer Option `isSome` checks | Pointer lifetime/nonnull decoding; this is not custom GIV (`some none`) |
| `Servo_AnimationValue_IsAttrTainted` / `CustomAnimatedValue::is_attr_tainted` | `tainted` | Wrapper bit is represented faithfully; custom value missing internally has false bit; noncustom values filtered by key |
| Per-entry OR and `std::any_of` | `entryChanged`, `changed` | Ordinary C++ Bool/iterator execution corresponds to these pure finite operations |
| Initialize change flag, skip without target or comparison pointer | `baseFlag` | Target-present case successfully reaches comparison; no provider failure/reentry changes its inputs |
| UpdateProperties unchanged-properties branch and final branch | `requestsRestyle` | Models invocation decision only, not queue insertion, execution or observed freshness |
| Rebuild and publish base then recompute after notification | `tick` | Intentionally modeled scheduler; NOT an extracted or proved Gecko scheduler |

`entry_decomposition` proves the pointer-presence guards cannot hide a metadata-only discrepancy when the original structural comparison permits equality. The primitive comparator remains arbitrary; it can be nonreflexive. `old_change_preserved` retains all native payload-change decisions, including missing/nonmissing mismatches. There is no global change to payload equality.

## Selected-key boundary

The scan reads only new entries, not removed old keys. `depends_only_on_new_keys` proves this locality; the removed-only witness exhibits a nonempty old entry with false change flag. No full old/new map-equivalence theorem is asserted. `selected_sample_metadata_after_request` requires membership of the selected `(key,value)` in new entries and custom-key classification. It does not assume all old keys survive. New map uniqueness/completeness and actual sample selection must be derived by a later caller/provider proof; the local theorem permits arbitrary finite entry lists, including duplicates, without concluding a full map invariant.

`EnsureBaseStyle` can return without insertion if no base is needed or no animating pseudo element exists; extraction can insert a null result. Empty `aProperties` does not need a pres context; a nonempty property list relies on the native assertion/readiness contract. A missing explicit keyframe endpoint may cause base selection but is not itself an entry of `mBaseValues`: its mapping to the selected new key is an external caller obligation. An explicit replacement not needing a base supplies no selected new entry, and is outside the selected-entry theorem. Scroll-delay/compositor and additive routes also have their own selection obligations.

## Scheduling boundary

`KeyframeEffect::RequestRestyle` may return without a target and calls its compositor only with a pres context and animation. `EffectCompositor::RequestRestyle` may return for disconnected context or absent pres shell, and can coalesce a pending request. The proof's `requestsRestyle` is only the call-site decision. The toy `tick` receives a notification assumed accepted and consumed, or a forced tick. Native queue ownership, dirty flags, rendering lifecycle, sample selection, base extraction/publication, reentry and observer timing are not proved.

The selected-sample theorem derives new metadata from the decision and an explicit *prior* sample/old-value coherence invariant. It does not take new output freshness as a premise. If that prior invariant already fails for another reason, the no-change case need not refresh. It covers one local transition, not arbitrary native animation histories. Root's browser evidence separately tests the paused implicit-endpoint path.

## Imported definitions and trust

`TaintValue.lean` and `EndpointModel.lean` are byte-identical copies from the accepted endpoint capsule (the latter changes only its module filename). `IMPORTS.json` binds their predecessor manifest. No imported theorem is counted as a new result. Native payload/URL-data observational quotient, FFI representation, memory/Arc lifetime, compiler, machine resource bounds and all provider/publication/scheduler obligations remain open. The small model tracks an attr bit; it does not prove URL parsing, IACVT behavior or the complete animation interpolation algorithm.

Fourteen complete function bindings plus complete source files establish exact source provenance and review context. They are not a verified C++/Rust-to-Lean translation. No native candidate compilation or browser execution is performed by this capsule.
