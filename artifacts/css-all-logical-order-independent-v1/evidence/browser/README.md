# CSSOM all-shorthand ordering diagnostic

The local browser at project checkpoint 68 preserves a pre-existing physical/logical property order when setProperty updates `all`. A fresh `all` expansion uses the opposite order. Eight diagnostic cases expose the difference for initial, inherit, revert and var(--all), with normal and important priority. Sixteen single-longhand and declaration-list controls pass; the harness completes normally. The diagnostic exits 1 for its eight assertions.

The test compares only padding-top/padding-block-start order with a fresh expansion. It does not prescribe an absolute longhand expansion order. CSSOM setProperty step 8 calls for a canonical shorthand expansion, and setting a declaration must place it after opposite-mapping declarations in its logical group. The resulting relational expectation is that the same expansion removes dependence on the prior pair order. [CSSOM](https://drafts.csswg.org/cssom/#dom-cssstyledeclaration-setproperty)

The precise definition of canonical order remains discussed in CSSWG issue 5741. Independent adjudication of this relational oracle and historical issues is pending. This evidence is not yet an accepted native fix, novelty claim, or proof of a rendering difference. The native-fix count remains 68.

The special all branch in prepare_for_update and update bypasses the ordinary logical-group reordering logic. Complete source snapshots accompany the raw events, test and recorded source/config/binary hashes. Root re-read the raw outcomes and verified every recorded live pin. The build is the shared project tree, not isolated upstream runtime. No native patch has been applied; the live diagnostic WPT remains uncommitted for possible inclusion with a reviewed fix.
