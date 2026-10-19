# Retained animation endpoint taint: bounded formal component

## Result

Five modules expose 25 audited results: seven readiness/bounds results, ten scan/decision/retention/history results and eight concrete witnesses. TaintValue is an unchanged imported model with only its module filename changed; Model defines this component's ordinary comparison, metadata scan and independent observation.

The repaired retention decision preserves all original changed decisions. Its only additional changed decision occurs when ordinary array comparison says equal and custom endpoint metadata observations differ. The theorem derives this exception; it does not assume endpoint taint equality. Both from/to bits are retained for arbitrary finite modeled replacement histories and all prefixes.

The model separates ordinary property/segment comparison from provenance. Ordinary key, payload and segment-core comparators are arbitrary Boolean functions; no global reflexivity, symmetry or payload equality is assumed. This deliberately accommodates the distinction between native PartialEq and full observational equality. Describing a native comparison result as equal payload still requires the source/quotient admission below. The mathematical metadata-retention result does not require the payload comparator to be sound, and does not establish payload correctness for an unsound comparator.

## Readiness and independent reference

`pairs` performs length-sensitive element comparison. `propertySame` compares property identity, custom classification and ordinary segment arrays; `segmentSame` compares core metadata and both nullable payload endpoints. `array_ready` derives equal array length from successful comparison. `indexed_reads_ready` derives each property access, same custom classification and both segment reads at every new-array index. `endpoint_presence` derives agreement of pointer-null and inner guaranteed-invalid presence. `counter_headroom` proves increment representability from an explicit length bound.

The metadata scan follows property order, skips non-custom properties, then compares both endpoint bits in segment order. The independent `observation` maps custom properties to lists of bit pairs and non-custom properties to None; it performs no pairwise comparison or early-return decision. `metadata_scan_iff` proves scan success exactly matches that independent observation under the derived ordinary shape. Lists provide finite traversal; the native index/counter lowering is a manual correspondence using the proved readiness facts, not a verified C++ translation.

`new_change_exact`, `decision_delta_exact`, and `retained_metadata` then connect the ordinary decision, the scan and selected array. `history_metadata` permits arbitrary finite input arrays and arbitrary initial arrays with the same metadata projection. It derives the relation after every update; `every_prefix_metadata` specializes to a common initial array. Histories model repeated calls that receive the listed computed arrays. They do not construct arrays from raw keyframes or prove delivery of those calls.

## Source identity

The sealed proposal was authenticated before reading: FREEZE 15000e7ba5e31072934bd59ab124d18d0876082b5e62e578531eb0d9dfabdde5, MANIFEST ad253012e5c2aab47932b163508241d6103271c18d6f352b914a682d93cd0e40, all 49 inputs checked. Its native.patch and complete original/candidate three-file sources are retained, along with complete equality/FFI context. SOURCE-BINDINGS.json contains 16 method/struct slices. The checker validates their bytes, signature starts and hashes and regenerates the exact three-file patch. These establish identity, not automatic semantic translation.

The candidate adds CustomAnimatedValue::is_attr_tainted, the Servo FFI dispatch, and the extra check in KeyframeEffect::UpdateProperties. It does not modify global equality. The C++ lambda returns false for a null endpoint; the Rust accessor returns false for inner guaranteed-invalid None. Non-custom FFI variants return false, and the C++ outer loop skips non-custom properties. See SOURCE-MAPPING.md for admissions and branch mapping.

The proposal is historical artifact source. This capsule neither applies it nor claims generated bindings compile, a candidate browser passed, or a later formatted source is byte-identical. Root owns those gates.

## Validation

Canonical and manifest-only relocated replay are performed outside this source capsule. The checker compiles all five modules, checks the exact 25-name axiom roster, and rejects proof placeholders/local axiom declarations in new modules. It pins the Lean executable and 5092 installed library files. Reported axioms may only be propext, Quot.sound and Classical.choice.

Two semantic mutants remove the from or to comparison in Model.segmentMeta. Each altered model must compile, and the common executable driver must compile and run. Its eight observations detect exactly the missing direction in both taint-addition and taint-removal histories; array-length, non-custom, null/invalid distinction and unchanged-value controls remain true. Definition or infrastructure failures do not count as detection. Predecessor mutant suites are not claimed rerun.

Separate replay receipts preserve command lines, outputs, initial development failures and integrity controls. Generated targets are removable after receipts are sealed. Kernel replay is a model result, not a full animation or CSS attr-taint conformance theorem.
