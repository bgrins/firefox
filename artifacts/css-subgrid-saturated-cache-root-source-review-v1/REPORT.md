# Root source review of saturated subgrid counts

Conditional GO for source/helper validation. Root authenticated all13 producer payloads, read the entire three-path patch/report and retained transfer excerpts, and independently matched nine historical source objects. Scratch Git apply/reverse checks and exact candidate/original postimages pass; the temporary checkout was removed. No native tree or index changed.

The parser now saturates both the per-repeat product and prefix sum. The cache field remains usize and its comment documents the changed upper-limit behavior. The consumer clamps its signed capacity to zero, compares the full-width count, subtracts only a smaller value, and narrows only that bounded difference. It preserves remainder and append loops. The difference is at most INT32_MAX and fits uint32_t on the supported32/64-bit widths.

The generic cache and guarded-consumer models supply the intended arithmetic relation under explicit count/group and primitive-operation contracts. Source-derived computed/animated/resolved/shared-memory transfers preserve the numeric cache; this review is a source inventory, not generated ABI compilation or whole-program refinement. Zero/negative boxed calc counts retain the separate range-policy defect. Invalid negative-cap placement/append behavior is outside this repair, even though this consumer's arithmetic is defined for negative caps.

A full native build, browser reproduction, isolated comparison, and relevant WPT patch are still required. This review accepts no new fix or severity classification.
