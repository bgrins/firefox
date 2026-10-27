# Proposed graph contract — implementation design, not a prescribed spec data structure

Use identities that distinguish the target/pseudo, sample and registration generation. Within one coherent sample:

| Node | Meaning | Required dependency distinction |
| --- | --- | --- |
| C(p) | Current winning computed property | Selected cascade winner; if animated, the final published stack result. A losing animation does not replace an important winner. |
| B(p) | No-animation base | Computed through the existing base-style route. Keep its context separate; never alias it to C(p) or an old sample. Literal bases isolate this boundary in the proposed probes. |
| S(p,i) | Prefix after effect i | Incoming underlying value is S(p,i−1), with S(p,0)=B(p). Same property, different node: this edge alone is not a cycle. |
| K(p,e,k) | Authored endpoint computation | Retained declaration and metadata, computed with current target providers C(q). Dynamic fallback dependencies carry the existing substitution state. |
| O | Native composition operation | Preserve exact endpoint/add/accumulate/interpolate order, implicit operands, same-offset selection and iteration operands supported by the actual producer. |

The value-dependency graph has C(p)→the winning publication, S→selected operation operands, K→C(q) for used `var(q)`, and S→previous prefix for additive/implicit work. A complete replace can sever the numeric prefix edge. The substitution-evaluation relation must additionally account for the computed-keyframe procedure, including endpoints that interval selection later does not use. Do not encode both relations by indiscriminately flattening all nodes to property names.

For SCC handling retain origin/winner selection, endpoint ownership, the active guarded-context stack, and marks until their defined owner returns. A numeric ready result, pending dependency, CSS invalidity, and an internal unsupported/error result are separate states. A pending cache is not a ready provider. Do not substitute a lower declaration, old sample, or registered initial for an internal error. Genuine CSS defaulting must preserve registration inheritance and metadata. Do not cancel unrelated properties or the Animation object when one value is invalid.

Recommended bounded production work: implement and test the acyclic current-provider contract with explicit node identities and no cached-value escape. Keep a full unresolved cyclic path distinguishable until its semantics are justified; this is a research integration boundary, not a production permission to reject otherwise valid CSS. The concrete cycle probes should establish interoperability evidence before selecting a blanket property-SCC policy. No new general graph framework is proposed.
