# Used non-type attribute fallback validation

The normal branch browser reproduced 19 failures in the new 34-case WPT. With only the reviewed two-file native repair applied, all 34 pass. All 154 existing regression subtests and six reftests pass in both runs with identical identities, outcomes and expectation metadata. The real native build succeeded. The exact fixture also passed the WPT lint API in an isolated root.

The failure is missing dependency edges when a missing or invalid non-type attr() primary selects a fallback. A fallback can produce a value while participating in a cycle; that value must not rescue the cyclic property. Coverage includes bare/raw-string reads, invalid/missing numeric and unit primaries, namespaces, self/mutual cycles, whitespace and extra tokens, ordinary font-size/line-height cycles, and attribute mutations. This is one defect with multiple cases. Original failing callbacks stop at their first assertion; later mutation and consuming-value checks complete only in the passing candidate.

The implementation shares primitive number parsing between substitution and graph admission. It reads the actual namespaced attribute to decide whether the fallback participates, preserving unused-fallback exclusion and attribute tracking. Typed recursion and the separate raw-nested false-cycle defect remain unchanged. Existing attr-cycle test expectations were preserved; passing that file is regression evidence, not a claim that its two historical raw-nested expectations match the current specification.

The guard-cycle Lean model supports the normalized cycle and fallback semantics. It is not a refinement proof of this Rust implementation, parser, namespace machinery or invalidation tracker. This validation adds no canonical Lean coverage credit.

Repair-v3 uses ParsedNamespace directly and supplies the complete shared numeric parser. Its branch patch is a small delta over a parent already containing numeric fix 499c0c6; literal upstream patch context therefore differs. The sealed upstream self-contained variant has matching new native helper behavior and the identical WPT, and explicitly includes the necessary numeric overlap. It has patch transport and syntax validation only; this branch run is not an upstream build result.

Both browser phases bind the same HEAD, exact native source bodies, normal binaries and application metadata. Only the independently checked BuildID may differ. Recorded source/index preservation and owned process/profile cleanup passed. Raw logs, assessments, resource inventories and commands remain alongside their immutable manifests. Large repeated epoch inventories remain local; their digests and preservation results are retained.

Acceptance and signing are separate steps after independent review. No fix count is increased by this validation record.
