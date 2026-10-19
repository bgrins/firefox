# Native removal loop admission

Keep the accepted public-storage and batching capsules unchanged. Authenticate the current 44-result public-storage checkpoint before compiling its copied modules.

Model the native changing declaration/importance/membership storage, numeric index, and local length directly. Each iteration reads the current declaration by index, advances only when keeping an entry, and decrements local length while retaining the index when deleting. A well-founded `length - index` measure terminates the model; an explicit fault outcome distinguishes absent reads on malformed storage from normal termination.

Derive exact equivalence to PublicStorage.removeLoop under its representation/prefix invariant, including final index/length, no read fault, iteration count and bounds. Then replace PublicAPI's shorthand loop with this source-shaped loop and compose query, singleton deletion and histories. Keep native usize, concrete container methods, compiler, caller callback readiness and immutable/changed flags outside the claim.

Bind complete retained remove_property, remove_declaration_at, first_declaration_to_remove and relevant query/storage helpers. Include genuine wrong-index/length mutation witnesses and exact theorem audits. No new broad finite corpus or live source changes.
