# Native payload review: MinMax and logarithm

This package proposes two three-path commits, in MinMax-then-log order. It is a review artifact, not an installer. Combined session 83012 remains pending; no acceptance, new ID, installed build or combined success is asserted.

1. `01-minmax.patch`: accepted pow source b291d6e9 → independently tested MinMax 065c05d8, plus the exact 18-case and 14-case MinMax WPT bodies.
2. `02-log.patch`: MinMax 065c05d8 → combined 0803cce1, plus the exact corrected 24-case logarithm WPT and deletion of `exp-log-compute.html.ini`.

The metadata file has exactly five target expected-FAIL annotations and no other expectations. Its captured bytes match the recorded HEAD ecfe313d. Removing those annotations leaves only an empty page header, so delete the complete file. Comparison metadata remains unchanged. The two unrelated MinMax legacy failures and four unresolved logarithm boundary controls are not publication edits. The four new cross-operator callbacks remain research-only and are excluded from both native commits.

The complete patches embed exact tested fixture bodies; MANIFEST records each capture, source preimage/postimage and explicit metadata deletion. No artifact, model, runner, ledger, provider or generated capture path belongs in either native commit. Intended-path lint and genuine WPT registration remain publication checks. Recheck actual source preimages and metadata before applying after the active owner restores them; this review did not inspect its live native overlay.

## Dependencies and attribution

The chosen source base is accepted pow 150 (2d18f8b4a4d7), preserving earlier hypot 149 (36b693fee75e) and round 145 (eb5208648811). These same-file predecessors are source lineage/context, not demonstrated semantic dependencies of the two new guards. The second patch depends on MinMax for its exact source preimage; the immutable integration check proves the independent patches commute in either order, so the logarithm behavior does not intrinsically require MinMax.

Accepted 119 (6a363fc372c9) supplies the existing nonfinite relative-length transport used by contextual MinMax evaluation and its zero-basis observers. Treat it as a tested semantic prerequisite for this contextual evidence; minimal independent cherry-pick requirements have not been experimentally isolated. Shared-branch runs also include held provider 120, which remains excluded and unchanged. No provider independence or clean-upstream execution is established. The four interaction probes intentionally require both operator repairs, without turning that interaction into a dependency of their independent scalar cases.

Scoped MinMax NaN-retention and logarithm dispatch models support the relevant guards. They do not prove full comparisons, IEEE operations, native refinement or arbitrary CSS behavior. Logarithm base-zero ambiguity and below-one zero/infinity boundaries remain outside the repair oracle.

Message drafts follow the established local No-bug convention and use the exact recorded Herald group #firefox-style-system-reviewers. The authoritative receipt covers the same calc file and representative css-values WPT/metadata paths; it is retained as historical reviewer evidence, not a newly executed lookup. Actual publication still requires successful reviewed validation and the research checkpoint sequence. No signer action is included.

Static preparation cf7326/0 authenticated captured source derivation in both orders, fixture identities and all five metadata targets against the original roster. This package does not merge historical raw runs into combined evidence.
