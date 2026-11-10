# Animation request conservation across selection and traversal

This supplies the missing abstract work-accounting component of the held #160 investigation. It does not prove the native drain terminates, establish computed-style correctness, or lift the hold. No native code or WPT changed and no new browser defect is claimed.

## Model and checked result

An obligation key contains a logical target/style lifetime, full pseudo type and argument, animation/transition cascade level, and request generation. Lifetime is a logical identity that must change when the relevant target/style state is destroyed and recreated; it is not a raw pointer. Generation identifies a fresh logical obligation, not necessarily EffectSet's existing animation-generation counter.

State distinguishes required work, queued requests, posted hints, in-flight work, installed work and retired work. Conservation means every required key remains represented in at least one of the latter five places. Selection transfers eligible queued work to hints; traversal admission transfers hints to in-flight work; completion transfers in-flight work to installed work. A new request made while older work is in flight survives completion. Ineligible requests and unadmitted hints remain pending.

`selectWithPosting` handles a further native boundary: selected work need not actually produce a hint. Its coverage theorem requires every selected request that cannot post a hint to have an allowed retirement. Without that premise, a concrete counterexample loses the obligation. Retirement records that work no longer needs styling; it is deliberately distinct from installation.

Every admitted transition preserves conservation, and so does every finite history. `Ready` is an accounting predicate: each required key has an installation or retirement record. Conserved work with no queued, hinted or in-flight obligations is ready in that sense. `ReadyFor` restricts this statement to keys relevant to a particular observation; unrelated or legitimately throttled work need not vanish. Neither predicate proves that an installed style has the right CSS value. That requires a separate interpretation of the installation record and a justified relevance relation.

The model is non-vacuous: requests for both cascade levels transfer through hints and in-flight work to installation, and that completed example is ready. Counterexamples show that queue emptiness alone is insufficient; collapsing the two levels into one retained representative loses work; and deleting a native-key queue entry after a hypothetical reentrant newer request can lose the newer generation. These are model counterexamples, not assertions that the inspected browser executes those faulty transitions.

The final isolated replay checks 30 theorem declarations and eight deliberately false propositions. The axiom audit admits only Lean's standard logical axioms, with no sorry or custom axiom. The controls reject empty-queue readiness, erasure after reentry, cascade-level collapse, unaccounted posting failure, clearing a new request during old completion, erasing functional-pseudo identity, erasing lifetime identity, and treating an old generation as fresh. They are false model claims, not mutated Rust executions. All compiled temporary outputs are removed by the replay.

## Native correspondence reviewed

Searchfox discovery uses revision 5a3f6397e61554eda92b0ec63ddd0ff752a22da2. The retained selection, request and C++ hint-posting bodies match exactly once in the corresponding current Git objects at 5f66e1974ac662623122a854b0facde0489f85c4. NATIVE.json pins those source objects and excerpts. The Rust hint-admission body is extracted from that same local revision after indexed discovery.

| Native operation | Accounting interpretation | Remaining premise |
| --- | --- | --- |
| EffectCompositor::RequestRestyle | Queue a target/full-pseudo/cascade request; the map's bool distinguishes posted from throttled work | Map coalescing must retain every still-relevant logical generation, or prove a newer snapshot subsumes it. Native keys do not contain this model's generation/lifetime tokens. |
| PreTraverseInSubtree's cascade update pass | May create requests before selection begins | Producer closure and request causes must be accounted for; the finite list of call sites does not bound activation count. |
| Eligible selection and PostRestyleEventForAnimations | Transfer queue coverage to the appropriate cascade hint | Eligibility and a true PreTraverse return do not prove hint insertion. |
| Missing pseudo element in PostRestyleEventForAnimations | Returns without posting | Justify retirement or another existing obligation that will recreate/style the target. Do not mark installed. |
| Missing ElementData in note_explicit_hints | Returns without inserting the hint | Same retirement/coverage obligation. The model does not assume absent style data can never be recreated. |
| Successful note_explicit_hints | Inserts the animation-level hint and marks dirty ancestry | Preserve full pseudo resolution and both cascade bits through the native-to-model mapping. |
| WillComposeStyle followed by iter.Remove | Removes the selected queue entry | Existing source review found no request-producing callee in this window. The guard does not prevent insertion; that no-new-request result, or snapshot-safe removal, remains necessary. |
| Wrong-document removal and full-document map clearing | Discard entries outside the applicable style domain | Establish retirement for the exact observation and lifetime. A clear operation is not automatically a successful drain. |
| Later traversal | Consume hints, compute and install styles | Identify actual admission and installation events. Queue removal and WillComposeStyle are not installation witnesses. |

The source already contained both failed-posting paths. This work makes their accounting obligation explicit; it does not reclassify them as new bugs. The earlier producer-closure audit remains the broader call-graph evidence. The current native bodies do not implement the full logical-key protocol directly, so no native refinement is claimed.

## What this changes for #160

There are now separate formal components for conserving obligations and ranking permitted productive phase work. They must be joined through the same native abstraction. In particular, coalescing animation and transition requests into one application-phase bit is sound only if that phase covers both levels and all relevant generations. The earlier phase theorem does not supply this automatically.

The next native discriminator should use the already passing producer-local combined candidate and an existing finite dependency fixture, not repeat the historical broad-handoff timeout. A ledger must join request identity/cause, selection, actual hint-post outcome, traversal admission, and installation or justified retirement. It must distinguish a failed post from a successful hint, preserve pseudo arguments and both cascade levels, and keep newer requests after selection visible. Existing trace data establishes the old feedback path but lacks enough of these fields to certify conservation.

Stable lifetime/pseudo mapping, justified retirement, semantic coalescing, bounded administrative work and closure of all normal-readmission producers remain open. This model allows arbitrarily many fresh requests; no termination follows from conservation. No cap, dropped work or weakened CSS oracle is proposed.

## Replay

Run `python3 -I -B check.py <new-output-directory>` from this directory. The driver authenticates the pinned Lean toolchain, compiles the model and axiom audit in a fresh temporary directory, and requires each negative control to fail with exactly its intended decide-false diagnostic. `run4/RESULT.json` is the final-source result. Earlier attempts retain ordinary elaboration failures; run2's checker correctly rejected a negative control that failed for a missing Decidable instance instead of a false proposition. That control was replaced by its concrete freshness condition. No failed run is counted as successful evidence.

FILES.json seals the artifact, excluding itself. Replaying generates a new output directory rather than overwriting the retained final result. This artifact does not import or modify the standalone CSS specification library.
