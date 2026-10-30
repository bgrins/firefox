# Corrected candidate74 evidence comparison

The first independent reviewer completed restoration verification but rejected the observation join: comparison.behavior returns tuple identities in nonempty differences, while persisted JSON decodes them as arrays. All three real lanes contain differences. Its equal-stream synthetic tests had empty differences and missed this serialization boundary.

This successor changes only the behavior result's JSON normalization before comparing it to the persisted record. No fields, order, messages, status, expected outcomes or native repair gates are removed. The normalized value also feeds the unchanged aggregate comparison. review.py and the complete restoration checks are byte-identical to the first reviewer. The first attempt, its failure, raw replay and restoration report remain untouched.

The existing eight synthetic cases remain. A separate saved-evidence check exercises all three real completed lanes and requires all85 signatures,15 passing target callbacks,56 PASS/18 FAIL,11 endings and the false preservation gate. A changed identity in a returned comparison record must still be rejected without modifying the actual evidence. Process absence is mocked only in this saved check; root's actual independent execution performs it and the full restored archive check.

Execution remains disabled until root binds the unchanged actual owner72027/67e6f7/a877de/0 and reseals this package. No native build or browser replay is needed for a serialization correction. This checker does not repair or accept the native union-plain regression.
