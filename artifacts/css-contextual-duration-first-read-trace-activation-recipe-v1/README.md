# Same-HEAD trace activation recipe

This is a root-executed binding recipe, not a new browser or signing owner. Preparation reads saved artifacts only. The V78 result records no commit and unchanged real index/canonical state; the actual root-reported terminal is 86468/d7968c/1. No signed-HEAD exception is needed.

Authenticate the disabled trace owner seal in EXPECTED.json before changing it. Capture current HEAD, the three canonical control hashes, raw index, root/nested ls-files flags, actual application metadata and the membership of all five role paths in the canonical pin map. Use the existing state helper and metadata helper named in the owner policy; retain GIT_OPTIONAL_LOCKS=0 and the existing environment-override refusals. The full owner guard remains authoritative before any source overlay/build. Do not infer current pin membership from historical build membership.

The expected HEAD is ecfe313d582a335c04d80bfd360fd3a591defdb7. CURRENT-EPOCH must be 563a559e97af05577b5cebdcaaccd605971202419533b5f99e29fe5cca6ac06f and raw index 8cacd9a9e06702179e36948109c2ed9ac370dcc903b2efadc3cac3f0438b70b6. OWNED/ROLE and the two flag hashes must equal EXPECTED.json. Preserve the 29 accepted payload records, held provider, three source preimages and the two additional layout preimages. The unchanged native-checkpoint path and digest are recorded in EXPECTED.json.

Fill only these admission fields: head; controls; prepared_application_metadata; prepared_flag_hashes; native_checkpoint; source_equivalence.current_revision; wpt.phase_revisions.candidate; role_current_unpinned_sources; fresh_restoration_binding. The candidate revision and current_revision equal the actual ecfe HEAD; the harness revision remains its existing ecfe value and original build remains 20ab. prepared_application_metadata is the existing helper's nine-field result, without the WPT-only build_revision/harness_revision/source_role projection. Its identity and entry_identity must match the fresh capture and frozen restoration terminal; all other fields must equal the original metadata. The frozen terminal's restored app is the original body936b/revision20ab, not the rebuilt candidate application.

role_current_unpinned_sources is exactly the subset of the five SOURCE-ROLES paths absent from CURRENT-EPOCH pins. For present roles, require the canonical pin and actual source hash equal the role base. For absent roles, retain the owner's both-Git-blob and actual source checks; the local overlay epoch adds a temporary identity/pin and restoration must return to the original canonical map. Historical role_build_unpinned_sources remains exactly PresShell.h; this is a separate fact.

fresh_restoration_binding should pin the saved runtime manifest and ROOT-TERMINAL, root raw-index-only refresh, failed signing result, and the new capture receipt. Verify the runtime terminal is 8127/bef82f/0, restoration/raw replay true, backup removed and result hash matched; the refresh joins that same runtime seal and changes only raw_index_observation.current. Verify the failed signer result is exactly committed=false, exit128 and real_index_and_canonical_state_unchanged=true. Add exact hashes of these receipt files to policy.references. Merely setting this field non-null is not evidence; root/reviewer must check the semantic joins above.

Preserve disabled POLICY.json and FILES.json as exact preimages outside the sealed owner before activation. Save a root activation receipt naming those preimages, the concrete capture and exact changed fields. Set both execution flags true and activation_pending empty only after the binding review. Recompute FILES.json while leaving every executable, fixture and source-role body identical. Regenerate a policy-only delta outside the owner. The same historical raw-index-only snapshot projection and strict harness comparison remain in force.

The saved-only check is:

```sh
python3 -I -B -S artifacts/css-contextual-duration-first-read-trace-browser-v1/check.py
```

Root may then use the existing `candidate.py --run <activated FILES SHA256>` interface. It performs the full guard internally before mutation; this recipe does not require a redundant separate live guard. The generated property-header SHA is checked after the actual linked build and after WPT. No browser/build/native/Git/index/canonical operations were performed while preparing this recipe.
