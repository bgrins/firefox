# Shared stylesheet media snapshot rebase

The pending repair stores each stylesheet wrapper's previous applicability on its collection entry. This avoids confusing distinct wrappers that share parsed contents. The existing native comparison recorded four passing and four failing callbacks before the repair, then eight passes afterward; that historical result is owned by `css-shared-sheet-media-history-native-pair-runtime-v1`.

The saved publisher's source preimages no longer all match the current branch. `stylist.rs` now contains the committed rollback repairs, and `glue.rs` has the root-identity candidate being validated separately. Replacing either file wholesale with the historical candidate would lose those changes.

`historical-native.patch` is derived from immutable revision `a6f39620516a4cf76a5dbf5208960adc79068cf1` and the three hash-verified historical candidate files. It applied with zero fuzz to temporary copies of the current sources. `current-native.patch` records the resulting three-file delta. Reversing that patch recovered all current source bytes exactly; the temporary directory was removed and live source files remained unchanged. `SOURCE.json` records each source hash and the current research HEAD.

This is a source-only rebase, not a new build or browser result. Before committing the production change, run the shared-sheet media and mutation-history WPTs against matched original and candidate builds and check relevant collection/cache controls. Keep the source changes and five WPT resources in one native commit, with this rebase and supporting research before it. The root-self overlay must either be committed first or the preimages explicitly updated.
