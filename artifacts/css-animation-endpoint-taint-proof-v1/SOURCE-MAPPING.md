# Source mapping and exact limits

| Native operation | Model or proof | Boundary |
|---|---|---|
| AnimationProperty::operator== | propertySame + length-sensitive pairs | Native property identity must determine IsCustom; mIsRunningOnCompositor and performance warnings are intentionally outside ordinary equality and our observation |
| AnimationPropertySegment::operator== | segmentSame | Core comparator abstracts offsets, timing and composite fields; no Float reflexivity assumed |
| AnimationValue::operator== / Servo_AnimationValue_DeepEqual | endpointSame / payloadSame | Outer None means null mServo; inner None means custom guaranteed-invalid value. Payload comparator must reflect the actual native ordinary comparison on admitted endpoints |
| CustomAnimatedValue::is_attr_tainted and FFI dispatch | tainted | The custom-property/provider/variant association is an admission; non-custom variants map to false. No FFI ABI, pointer lifetime or Rust representation proof |
| UpdateProperties outer/inner loops | metadataScan + indexed_reads_ready | Pure immutable array views, consistent equality and IsCustom, faithful indexed traversal. Early exit may stop after first mismatch; it does not change the Boolean decision |
| propertiesChanged branch and mProperties move | changed / retain | Projects only endpoint metadata, not compositor state, performance flags, base maps, notifications or restyle effects |
| Repeated UpdateProperties calls | run / history_metadata | Supplied computed replacement arrays and delivered calls; no raw-keyframe scheduler theorem |

## What readiness closes

Successful ordinary comparison derives the array/segment lengths, classification agreement and all reads admitted by the new loop's index ranges. This is not a premise that the extra comparison is already safe. Finite list recursion terminates, and counter_headroom explains the machine increment obligation once length representability is supplied. The capsule does not translate nsTArray, size_t, memory access or native pointer safety. Null pointers are never passed to the modeled taint read, consistent with the source short-circuit guard. Inner guaranteed-invalid None is distinct from a null pointer in ordinary comparison even though both taint reads yield false.

## Native assumptions still open

1. **Computed providers and identity.** BuildProperties, raw-keyframe replacement, registrations, CSS-wide initial/inherit handling and property-to-AnimationValue variant association must produce the arrays represented here. Wrong-variant or unrelated-name endpoints are not silently accepted as correctly modeled custom values. Provider/scheduler correctness is not inferred from source hashes.
2. **Payload quotient.** Native equality omits attr taint and URL metadata. The new comparison accounts only for attr taint. The model's payload comparator may be arbitrary, so no theorem proves full native value equality, URL-data equivalence, correct interpolation or arbitrary observer substitution. Existing equality choices for other consumers are unchanged.
3. **Publication and lifecycle.** EnsureBaseStyles executes before the retain/replace branch and has its own equality-dependent notification. The model does not prove its effects or exclude reentry by a global theorem. Likewise UpdateEffectSet, cumulative changes, compositor flags, notifications and RequestRestyle are outside the selected-array projection. Actual memory stability and application of the selected endpoints to computed style remain admissions.
4. **Histories.** The history theorem is for a finite sequence of admitted arrays reaching this update point. It does not prove that equal raw keyframes with changed external inputs trigger a new call, nor that all public animation operations route here. It does not prove event ordering or eventual delivery.
5. **URL/CSS semantics.** No URL parser, substitution graph, interval taint propagation or CSS-wide provider is modeled here. The frozen proposal supplies a normative/runtime target with constant endpoints; this component proves the local retention obligation needed by that target, not the full target.
6. **Standalone dependencies.** The proposal's one-site map publication prerequisite remains separate. This proof neither removes that dependency nor establishes an isolated upstream browser result. Mixed-taint interpolation, additive composition, transition creation, SMIL and base-style change scheduling remain outside.

The earlier TaintShortcut model is imported byte-for-byte under filename TaintValue solely for Value and payloadSame. No inherited theorem is relabeled as new and no earlier native source binding is transferred implicitly. Proposal manifests and exact copied files bind this component's separate source version.
