# Independent censorship-boundary review

Scoped GO for the conditional mathematical results. The four declarations prove properties of the existing rational/extended-scalar model, not IEEE arithmetic, Stylo call sites, or another browser defect. No canonical registration or theorem-count change is made by this review.

`late_nan_offset` uses infectious NaN addition followed by final censorship and clipping, with bounds retaining zero. `early_nan_offset` first replaces NaN by a finite zero; ordinary rational addition then returns the offset when the outer bounds retain it. The arbitrary inner bounds are harmless here because NaN censorship is definitionally zero, independent of those bounds. The proof does not silently require valid inner bounds.

`final_equivalence_not_contextual` combines equal standalone final observations for NaN and positive zero with an enclosing-addition counterexample. The nonzero-offset and both retained-value hypotheses make the distinction substantive; the result does not assert that every context distinguishes the values. `zero_basis_infinity_offset` covers either abstract infinity sign and either abstract zero sign, because their product is NaN. Its early branch censors the product before addition. This differs deliberately from the concrete infinity control, which censors infinity before multiplication; the report distinguishes the two placements correctly.

The generated controls separately establish the concrete late result0 and early result1 for bounds[0,2], offset1. Their three negations compile. Each attempted contrary equality is rewritten to0=1 and rejected by kernel reduction, not a syntax or unresolved-reduction error. The final raw error logs explicitly say that `decide` proved the proposition false. Earlier authoring and reduction-diagnostic failures remain retained; their superseded PASS label supplies no negative-control evidence.

The replay authenticates the compiler, Boundary source and twelve reachable project dependency sources. I independently checked the project import ordering, then ran the retained replay into a new owned output directory. Each dependency is rebuilt in an owned temporary directory with LEAN_PATH restricted to that directory, two threads and55-second per-process timeout. The bundled standard library remains a trusted toolchain component. The four axiom reports match the original final report and contain only standard Lean axioms; no sorry or custom axiom is introduced. Temporary sources and compiler products are removed by the replay, and dependency hashes are checked again.

The useful native obligation is contextual equivalence when moving censorship across arithmetic, not mere equality of isolated final values. Unit resolution, provider freshness, parser simplification, concrete machine rounding/saturation, property processing and native coverage remain outside this capsule. In particular, these exact extended-value operations do not prove that any specific Sign implementation preserves nonfinite values until the correct boundary.

Replay command:

```
python3 -B -I -S artifacts/css-intermediate-censorship-boundary-v1/replay.py --output /Users/bgrins/code/firefox/artifacts/css-intermediate-censorship-boundary-review-v1/replay
```

This output path was absent at execution. CHECK.json records the actual terminal result and log equality. No native, browser, canonical-library or index mutation was performed.
