# Independent count and iterator source review

Status: source design supported under the explicit representation premises below. Final expanded paired runtime and packaging passed; the conditional iterator/count proof reviews are sealed separately below. Their joint proof bridge remains separate. The label-only iterator is not approved as a standalone upstream repair: the pre-existing incorrect length can cause its newly unique iterator to exhaust below the advertised count. Keep the old iterator review as a historical checkpoint.

## Exact candidate

Retained four complete variants authenticate against SOURCE-PINS.json: original d29360da7b8e104a7957ea9db068b25222dbcb3514c5e4999f812c1e812cf7a6; iterator-only 63cd8e85941276bceffd891bf93a213a37dad25c8b21ad375951a6993a34bcb4; count-only ce662e816f73df30b55718fa14e8c44586c94e130fe147c13a696788b41339d5; combined 23f550aec8661e04fd4715daf5161deac341f4f5a9ed7c1384b2292590eb8ca6.

Count repair makes two semantic changes: Inner::insert updates len by the difference between new Some presence and old effective Some presence, and get_index filters None before nth. The raw iterator retains tombstones. Comments describe the new live count. The separate iterator patch labels the outer traversal loop and targets it on a descendant-owned key.

## Invariant and all construction branches

Let E(n) map each key to its nearest owning node's Option. The intended invariant is len(n) = number of keys whose E(n) is Some. It does not count distinct stored keys or all own map entries.

- EMPTY starts with empty own/parent and len zero.
- On insert, self.get(name) reads the effective old value before mutation. Only this key changes. False→True adds one, True→False subtracts one, equal presence leaves len unchanged. This covers first insertion, replacing a present own/ancestor value, removing it, repeated removal, and restoring an own/ancestor tombstone.
- The Arc-unique branch mutates that node. The make_mut branch clones its complete own map, parent pointer and len before the same update. Assuming correct Arc/IndexMap clone behavior, both preserve E and len until the single-key update.
- The shared-node expansion branch starts with empty own, parent=self, and len=self.len. Its initial effective map equals the old map. The same single-key update therefore preserves the invariant. The 8-entry threshold and 4-ancestor cap concern chain storage and are unchanged.
- The equal-value fast return preserves effective presence. It does not need all payload values to have reflexive equality: Option equality returning true already entails matching presence; NaN or unequal taint may affect whether this optimization is taken, but not the count delta proof.
- Cloning, shrink_to_fit and unchanged retained parent maps preserve the invariant under their provider contracts. Parent ownership is immutable to an existing child: a later mutation through another shared Arc owner takes a copy-on-write branch.

None remains in own_properties to mask ancestral values. Erasing it or counting serialized text would be wrong. A valid empty value is Some and remains counted; its CSS text may be empty even though it is not guaranteed-invalid. Removing a missing key can leave a stored None while maintaining count zero.

## Iterator/index composition

With corrected iteration and unique per-node keys, raw iteration yields each key once at its nearest owner, including None. Filtering Some yields exactly the live reference map in surviving traversal order. Therefore i < len implies nth(i) is Some, and i >= len returns None through the guard.

With the original iterator, the filtered stream can still contain shadowed ancestors. However, every nearest effective Some appears at least once, so its length is at least the correct live count. Count-only therefore establishes no below-len exhaustion on coherent finite chains, although it can return duplicate/wrong ancestor names and omit other names from the truncated prefix. It does not claim to repair shadowing.

With corrected iteration but old count, that lower-bound guarantee fails. The retained literal source-shaped witness constructs grandparent target+8 outer names; middle target=None+8 middle names; leaf restores target. Old lengths are 9,17,18 while the leaf has 17 live names. The corrected raw iterator has only 17 entries, so index17 is below len18 but has no entry. Corrected lengths are 9,16,17. This witness is executable Python plus an independent overlay map, not native Rust or universal proof.

## Caller audit and bounds

Read complete frozen map, ComputedCustomProperties methods, cascade initialization/finalization, Servo count/name exports and nsComputedDOMStyle Length/IndexedGetter. Searchfox discovery identifies the map type owners and field consumers; indexed current source may differ from local snapshots, so it is discovery evidence only. Exact local/historical sources are retained separately. Searchfox CLI lacks --permalink in this environment; the failed attempt is not treated as source evidence.

- `ComputedCustomProperties::property_at` first asks inherited.get_index(index), then uses index-inherited.len for the non-inherited map. Corrected uniqueness+count prove that the fallback is taken only when index >= inherited.len, so subtraction cannot underflow. Count-only's lower-bound argument also suffices for this arithmetic safety, without establishing returned-name correctness.
- `Servo_GetCustomPropertiesCount` sums the two counts after u32 casts. `Servo_GetCustomPropertyNameAt` returns the selected name without examining the Option. `nsComputedDOMStyle::Length` adds the built-in count; IndexedGetter reports a found custom index and starts its name with '--', explaining the bare '--' diagnostic when the old inconsistent representation returns no name.
- `is_empty` is len==0; ComputedCustomProperties folds the two maps. The discovered production consumer is the root cascade assertion. Live-empty maps may retain tombstones, which is consistent with semantic emptiness; storage emptiness is a different property. The count change does not erase these masks or flatten chains.
- Inner equality's early len check becomes a live-count check, while the existing own/order/value/parent comparisons remain. It still may conservatively distinguish semantically equal maps; no new semantic map equality theorem is claimed.

Machine bounds remain explicit: a decrement is safe when the old presence implies len>=1 under the invariant. Increment requires live-count headroom and normal successful storage mutation. usize bounds, u32 conversion/sum headroom (including built-in properties), allocation/panic behavior, Arc/IndexMap semantics, immutable borrowing and compiler lowering are not universally proved here. Two-map CSSOM uniqueness additionally requires disjoint live-name domains and consistent registration routing across updates. map_mut and get use the supplied registration.inherits() branch; insert/remove do not clean the opposite map. get_for_cssom prefers inherited while count/index concatenate both maps. This repair does not establish registration/cache lifetime coherence or arbitrary re-registration behavior. The mixed-map WPT exercises offsets under stable registrations, not that lifetime invariant.

## Normative oracle and test scope

Current CSSOM getComputedStyle appends all custom properties with non-guaranteed-invalid computed values; length/indexed names expose those declarations. Ordering remains unspecified, so sorted name comparisons are correct. CSS Variables makes unregistered initial guaranteed-invalid; missing substitution without fallback and cycles also yield invalidity. Guaranteed-invalid serializes empty but a valid empty token sequence remains a value. Registration with syntax '*' and no supplied initial is allowed and has guaranteed-invalid initial. Primary HTML and retrieval hashes are retained under spec/.

A control-oracle qualification was sent to root: the historical valid-empty case expects an exact empty serialization, while current Variables serialization prose specifies a single-space exception for empty custom properties. The enumeration expectation is unambiguous. The final count WPT should compare trimmed text for that valid-empty control while retaining exact names/count, and leave GIV empty assertions exact. This avoids encoding an unrelated serialization behavior; it is not adjudication of a new bug.

The initial 8-case flat probe always has a sentinel. Two additional focused cases were requested before final packaging: last-live-value removal/restoration without a sentinel, and mixed inherited/non-inherited registration maps through zero/one/both-live transitions. These exercise actual zero-count and offset branches absent from the initial controls.

## Historical runtime and packaging decision

Independent raw inspection of the 39-case matrix finds original30PASS9FAIL, iterator-only33PASS6FAIL, count-only36PASS3FAIL, combined39PASS; each has7OK harnesses and the same39subtest identities. Builds succeed and binary associations match. Count-only adds no newly failing row in this set. The iterator-only restoration row was already a failing row on original; its failure changes to a count/empty-name boundary, so it must not be described simply as a newly failing test. MATRIX39-REVIEW.json retains exact failures.

The historical original runner omitted an explicit before/after pin for the clean native map; its build driver pins source after compilation. Final expanded pairing must pin the map explicitly regardless of dirty status. Shared-tree runtime is not isolated-upstream runtime.

Recommended main-stack order: count/presence repair first, then iterator shadow skipping. The independently applicable upstream iterator alternative must include the necessary count/filter support and relevant WPTs, with that support identified in the ledger. Do not advertise the label-only upstream artifact as safe merely because the seven all-Some tests pass. Count-only may land for its valid subset while the remaining duplicate-shadowing defect is explicit; combined is the target for complete live-index correspondence on admitted chains. Final exact inventories and all apply/reverse paths passed; see packaging/INDEPENDENT-APPLY.json and packaging/STANDALONE-PACKAGING.json.
