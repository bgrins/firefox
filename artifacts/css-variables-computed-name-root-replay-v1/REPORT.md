# Root computed-name review and replay

Root read the complete Names.lean, Examples.lean, replay.py and exact expected logs, authenticated every sealed input, and independently replayed the capsule. Session 83562 completed with exit 0 (launch c93c97, terminal 44b7ed). The 25 declaration inspections, 12 examples, three decisive false controls and 18 negative-log gate checks pass. Shared canonical imports remained unchanged and the owned temporary compilation directory was removed.

The source review confirms full value/state equality for embedded old bindings, finite remaining-binding termination, active-cycle checking before base lookup, and state threading through computed-name decoding, target lookup and fallback. Root checked current primary var replacement steps 2 and 4: a failed name parse makes the primary result invalid, allowing fallback. The normalized name-token adapter is an explicit premise; neither its exactness field nor the generic parser-parametric lemmas prove raw CSS parsing. No native correspondence, animated-provider correctness or cross-request caching theorem is established.

The source is suitable for a canonical integration proposal under these limits. It has not been integrated and adds no canonical/normative coverage count or accepted browser fix. The separate native support audit and prospective browser probes remain pending.

Primary algorithm: https://drafts.csswg.org/css-variables-1/#replace-a-var-function
