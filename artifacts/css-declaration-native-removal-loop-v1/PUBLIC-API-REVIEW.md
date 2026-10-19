# Review of the nine added PublicAPI lemmas

Parent attested CHECKPOINT SHA-256 2667921b7a4804190b0af210bb88aaa9e5990de8a4ef7f828d88be1ab59ad2f3 and unchanged replay SHA-256 5e0662187e3efcac16483b4c1730833bfb678e5157221ea2f06d34c76807e9e6 against HEAD bb029748eaa6 (introduced by signed 82f7308ddbb5). All four module hashes were verified before compilation. The earlier independent 35-result review remains immutable and does not retrospectively cover these nine additions.

All nine lemmas were read. No issue was found with their limited claims:

- `absent_membership_query` and `query_refinement` correctly derive the native non-shorthand membership early return from the exact representation relation. They do not assume absence merely from a malformed set.
- `singleton_filter` uses unique IDs to remove precisely one matching declaration. `remove_refinement` correctly separates this branch from shorthand filtering and requires the cached first-match certificate.
- `cached_callback_refinement` permits payload/priority changes only if represented storage and ordered ID lists are preserved. It neither proves this callback frame condition nor admits reordering/removal merely because the target still exists.
- `queried_api_refinement` covers no-match and matched branches without claiming malformed-storage behavior.
- `public_step_refinement`, `public_api_history`, and `public_api_prefix` compose parser-priority publication, queried removal and clear. These are pure modeled histories, not all CSSOM operations or arbitrary callbacks. Declaration-return/change bits, immutable flags and animation constructors remain outside.

The new removal-loop component replaces the shorthand ghost-suffix execution with direct current-vector indexed execution and then transfers these same API/history contracts. Concrete native containers, iterator implementation, integer bounds, metadata predicates and normal completion remain source admissions.
