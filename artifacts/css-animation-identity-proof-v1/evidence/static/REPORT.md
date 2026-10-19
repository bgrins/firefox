# Animation property identity: provider follow-up

Static source audit, 19 October 2026. No new Firefox defect, native execution,
browser result or universal proof is claimed. This extends the earlier
animation-map constructor admission audit without changing its frozen record.

## Constructor obligation

`PropertyDeclarationBlock::from_animation_value_map` populates membership from
map keys and declarations from `animation_value.uncompute()`. Key uniqueness
therefore needs the additional invariant that each value has the same property
identity as its key. Generated longhand tags and custom names implement that
identity; equality of payloads is unnecessary.

## Providers inspected

| Boundary | Source evidence | Remaining obligation |
| --- | --- | --- |
| Computed keyframe entry | `Servo_GetComputedKeyframeValues` passes `value.id()` with `Some(value.clone())` to its append closure. The explicit property path supplies only `None`. | Rust/C++ ID conversion, cloning and generated representation preserve identity. |
| Logical properties | `AnimationValue::from_declaration` writes the physical longhand tag before the caller derives the entry key. CSS-wide keywords select a physical variant. `from_computed_values` constructs the requested physical variant or returns no value. | Generated physical mapping and layout are correct; numeric values and writing-mode dependency invalidation are separate obligations. |
| Keyframe entries | `GetAnimationPropertiesFromKeyframes` copies each computed property's key and value together. | Upstream computed entries satisfy the relation; ranged NaN offsets are skipped and other offsets are valid. |
| Segment grouping | `BuildSegmentsFromValueEntries` sorts by property then offset. Ordinary endpoints come from selected entries in a property group. Missing endpoint helpers copy the existing entry and leave the synthesized endpoint absent. | Prove the changing `i`/`j` loop preserves same-property endpoints, including group transitions, duplicate boundary offsets and singleton groups. The comparator/grouping and non-NaN offset premises matter. |
| Base cache | `EnsureBaseStyles` clears and repopulates `mBaseValues`. `EnsureBaseStyle` passes `aProperty.mProperty` to `Servo_ComputedValues_ExtractAnimationValue` and inserts under that same key. The Rust extractor calls `from_computed_values` with the decoded identity. | Cache/table lookup and FFI preserve key association. A missing value can suppress composition; that is distinct from returning a different property's value. |
| Transition replacement | `ReplaceTransitionStartValue` extracts the replacement value's property and compares it to the owning `mProperties[0].mProperty` before assigning the endpoint. | Property conversion/equality and `uncompute` preserve the checked identity. Script-modified transitions do not bypass this check. |
| Selected segment | `KeyframeEffect::ComposeStyle` selects within the owning property's segment array; `ComposeStyleRule` passes that owner, selected segment and same owner's last segment. | Nonempty/bounded segment storage and provider invariant. |
| Composition | `composite_endpoint` uses the endpoint, underlying value, or their arithmetic result. `accumulate_endpoint` uses the composited endpoint, original endpoint or a result with the last value. `compose_animation_segment` selects these values or interpolates them, falling back to one endpoint. | Derive preservation through every branch from same-property inputs and successful arithmetic; also prove required option values exist before `unwrap`/`expect`. |
| Arithmetic and output | Generated `AnimationValue::animate` rejects unequal longhand tags and writes the original tag on success. `CustomAnimatedValue::animate` checks names and copies the name. Clone, zero and uncompute preserve tag/name in inspected generated branches. | Unsafe layout, code generation, custom-name/atom conversion and compiler correctness remain trusted. A tag mismatch panics, so an arbitrary-input totality theorem would be false. |
| Map update | `Servo_AnimationCompose` looks up the current map/base value by the decoded owner, composes, and inserts its result under that owner. | Induct over successive effects to preserve the map invariant; initialize from the fresh empty map described in the predecessor audit. |

The inspected `KeyframeEffect` mutations replace the property array with newly
built properties, clone an existing array, or update compositor/performance flags.
The exceptional transition endpoint mutation has the explicit identity guard
above. This inspection is not a whole-program alias/write-set proof.

## Negative result and next formal step

No reachable key/value mismatch emerged from these paths. In particular, logical
normalization happens before key derivation for non-null keyframe values, and
transition replacement cannot silently install a different property's endpoint.
These observations narrow the admission; they do not remove it from the public
storage theorem.

The next useful component is an identity relation over optional endpoint values,
source-shaped endpoint/accumulation/composition operations, and finite map update
histories. Arithmetic success must preserve identity; failures must follow the
actual fallback or panic path. Then compose that result with a separately proved
segment grouping invariant and constructor representation theorem. Retain the
generated layout and native container admissions explicitly.

For the grouping proof, non-NaN offsets cannot be silently dropped: the loop's
property-boundary branches distinguish `< 1` from `>= 1`. Neither holds for NaN.
The keyframe provider skips ranged NaN entries, but the complete source-to-offset
validity chain still needs a proof. This is an obligation, not a claimed reachable
counterexample or newly discovered browser bug.

## Evidence scope

`SOURCES.json` identifies complete local source snapshots and their HEAD blobs.
Searchfox was used to discover the actual provider definitions and callers;
local source bodies were then inspected. The checker verifies source identity,
the closed file roster and unchanged live source when requested. It does not
validate the prose inference or establish any behavioral theorem. No new WPT is
appropriate without an observable discrepancy or a selected regression risk.
