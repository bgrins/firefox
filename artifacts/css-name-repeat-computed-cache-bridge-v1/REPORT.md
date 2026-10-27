# Computed NameRepeat cache: reuse and conversion obligations

The existing 19-result subgrid chain covers the cache after Context computation, provided each entry supplies its final computed count. No new saturation theorem or new theorem credit is needed. This artifact checks a small conversion adapter and counterexamples; it does not modify the canonical library or establish native refinement.

| Existing result | Reuse after Context computation |
| --- | --- |
| `CountTransport.cache_correct` | The saturated multiply/add fold equals the machine cap applied to the total fixed contribution. |
| `GuardedConsumer.guarded_transport` | The remaining-capacity branch equals mathematical subtraction clamped at zero. This permits a full usize storage cap above the signed native line cap. |
| `SequencePrefix.sequence_prefix` | Ordered bounded output equals the corresponding conceptual prefix. |
| `WholeAutofill.observed_prefix` | The available capacity comes from the final supplied computed counts. |
| `WholeAutofill.resolved_nonexhausted` | Auto-fill contributes whole pattern copies followed by the remaining fixed groups and unnamed padding. Its admitted-input premises still apply. |

`ComputedCache.lean` maps repeat-count tokens through an arbitrary supplied evaluator, preserves ordinary groups and auto-fill patterns, then constructs the cache. Five generic anonymous checks instantiate existing results, prove that the specified placeholder cannot affect rebuilding, and check an inverse conversion that stores computed counts as inline counts. The inverse uses the identity evaluator: native `Integer` conversion and inheritance must establish that premise themselves.

The final replay is `replay-v2/CHECK.json`: all 19 existing results rebuild, five generic adapter checks and nine closed positive checks compile, and five intentionally false claims are rejected by kernel `decide`. Compiler products were created in a temporary directory and removed. No native source, index, browser, build, or canonical library actions were performed.

The closed context sequence uses one unchanged specified expression containing an opaque repeat token. Only the supplied evaluator changes, giving counts 2 → 3 → 1 → 2. Fresh computation preserves the expected trailing group. A stale count-2 cache reused with count 3 replaces that trailing group with auto-fill; a stale count-3 cache reused with count 1 underfills it. Consuming the specified zero placeholder also replaces the trailing group. Other checks cover unnamed groups, 32/64-bit saturation, no auto-fill, and whole-pattern remainder padding. These are model counterexamples, not additional observed Firefox defects.

Required native correspondence remains:

- Compute every entry using the actual `Context` before constructing the cache; invalidation must recompute when a count dependency changes. Font/provider computation and invalidation are outside this model.
- Use the supplied final positive computed count. Establish positivity before converting signed counts to usize; debug assertions alone do not prove that native premise.
- Count an ordinary group as one even when it has no names; multiply fixed pattern length by its count with saturation; contribute zero for auto-fill; saturate the complete sum. Pattern order and existing CSS admission constraints must be preserved.
- `from_computed` must retain computed counts for inheritance. Recomputing the resulting inline specified values must preserve those counts, entries and cache; it must not reintroduce the original context-dependent expression.
- The specified zero cache is unused storage. No native, resolved-value, serialization or other consumer may treat it as the computed cache. Every relevant route must obtain the computed form first.
- Preserve the existing native remaining-capacity guard, widths, layout/ABI, allocation behavior and resolved-list bounds. The mathematical list model does not establish these properties of the proposed Rust implementation.

`replay-v1` records the initial passing formulation, whose source SHA256 was `065618074d70db67b17c5c718c06e873850648918e263351385dead8f6087a07`. That formulation changed a supplied count embedded in the specified value. Before sealing, it was strengthened to the fixed-expression/evaluator formulation above; only `replay-v2` validates the final source. The earlier logs are retained as provenance.

Reproduce with `python3 -I -S -B artifacts/css-name-repeat-computed-cache-bridge-v1/replay.py --output /absolute/path/to/a/new/output-directory`. Inputs and referenced archive members are authenticated before compilation. The replay requires the pinned local Lean executable. This artifact adds zero theorem credit and makes no claim of new CSS specification coverage.
