# Candidate-v2 operation correspondence and remaining admissions

| Actual candidate symbol/field | Mathematical representation | What is established / what remains |
|---|---|---|
| ComputedSubstitutionFunctions.attributes | NamespaceBuckets.Buckets | Namespace→OwnMap with local-name inner keys. Flattening and writes are proved; OwnMap/hash implementation and actual Namespace equality are not modeled |
| insert_attr/get_attr/remove_attr | writeBucket / flatten lookup / tombstone write | All three carry the same resolved namespace. `remove_attr` writes an invalid entry rather than deleting it; the model preserves that distinction. Native lookup flattens absent and invalid into None |
| SeenSubstitutionFunctions.attr | namespace→seen-name collection | Namespace-bucket membership and insertion are proved equivalent to qualified membership. The model's list may hold duplicates; native HashSet does not, but only membership is observed by these theorems |
| Cascade::update_attributes_map | bucketPreload | Typed references only; Unknown exits before creating a seen entry; successful first admitted query stores in that namespace bucket. Failed query still marks that key seen. Provider/parsing return is an arbitrary supplied result, not assumed correct CSS |
| AttributeData::namespace | resolveKey | Known yields its resolved Namespace; Unknown yields None. Prefix aliases are equal only when URI resolution yields equal namespace tokens |
| VarType::Attr(Name, Namespace) | Node.attr Key | The explicit namespace field prevents structural equality from collapsing distinct namespaces. Custom/NonCustom remain separate enum variants |
| OrderIndexMap.attr | nested namespace→name→index map | Key separation is represented. Actual counter allocation must still prove distinct discovered nodes receive distinct numeric indexes; no bound/overflow or Tarjan proof is supplied here |
| visit_value_references attr branch | planAttribute / qualified graph edge | Can-chain check occurs first. Unknown then queues the fallback and continues without a primary node. Known queries/inserts/visits the same namespace. Correct used-edge selection and fallback semantics beyond this branch remain open |
| Context::handle_loop | invalidateNode / invalidateComponent | Attr arm passes its stored namespace to remove_attr. Theorems identify exactly which attribute entries an arbitrary supplied component list invalidates; they do not certify how native constructs that component |
| traverse shortcut and resolution calls | applyArguments | All calls for Attr carry Some(namespace), Custom carries None. NonCustom has its separate apply path. Roundtrip proof makes Some(null namespace) distinct from None/custom |
| substitute_references_if_needed_and_apply | qualified store/invalidate target | Replaces the kind parameter with Option<&Namespace>; attribute failure/success use that namespace. Registered-custom behavior remains in the None branch. Complete evaluator effects are not formalized |
| substitution Attr(Type) branch | qualified read | Outside container queries it retrieves by name plus namespace. Container query bypass is retained and not included in the cache-map claim |

## Required admission checks for a native correctness claim

- Every typed attribute preload, recursive discovery, map access, SCC member, SCC index key, invalidation and final apply must retain the same resolved URI. The retained source inspection covers the changed call sites in the two candidate files; a full repository consumer/build audit remains root's responsibility.
- Constructors and callers must never use None to represent the null attribute namespace. Unknown attribute namespaces must not reach the custom-property apply path. The dispatch theorem proves the API distinction, not arbitrary caller compliance.
- Every semantic graph node admitted to traversal must correspond to one native index, and every visited edge must correspond to the actually used substitution dependency. Fresh indices require a bounded machine arithmetic argument. Reachability/SCC identity preservation is useful only after these conditions are met.
- Stable provider/parse results are not needed for nonclobber: arbitrary values and invalidations are allowed. They are needed for a stronger final-value CSS theorem, which is not claimed.
- Namespace-bucket allocation can change iteration order and memory cost. The component does not assert traversal-order independence of the entire coupled evaluator, ABI compatibility, or performance neutrality.

The baseline's name-only substitution map cannot encode two distinct namespaced literal values at the same local name. That unconditional impossibility result remains alongside the repaired representation, rather than being removed after proposing the fix.
