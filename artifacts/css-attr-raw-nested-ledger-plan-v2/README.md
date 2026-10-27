# Executable raw fix138 ledger handoff

update.py is a parameterized adaptation of signing-v11/update-ledgers.py. It has not been executed. It will mutate exactly the five designated live ledgers plus the explicitly supplied signing-v13 CURRENT-EPOCH.json, and create preimage/evidence/receipt artifacts in that signing directory. It performs no Git mutation, staging, commit, build or browser launch. Root must review and invoke it only after green fresh comparison, installation, acceptance and signed commits.

Example invocation, with actual existing paths substituted:

    python3 -I -S -B artifacts/css-attr-raw-nested-ledger-plan-v2/update.py \
      --signing-dir artifacts/css-local-signing-20261027-v13 \
      --acceptance ACTUAL_ACCEPTANCE_JSON \
      --native-receipt ACTUAL_NATIVE_FIX_RECEIPT \
      --tools-receipt ACTUAL_RAW_TOOLS_RECEIPT \
      --validation-receipt ACTUAL_RAW_VALIDATION_RECEIPT \
      --epoch artifacts/css-local-signing-20261027-v13/CURRENT-EPOCH.json \
      --epoch-sha256 ACTUAL_EPOCH_SHA256 \
      --original-assessment ACTUAL_ORIGINAL_ASSESSMENT \
      --candidate-assessment ACTUAL_CANDIDATE_ASSESSMENT

The epoch must be the signing directory's CURRENT-EPOCH.json. Every output commit ID is read from an actual receipt. Native parent must equal validation commit; validation parent must equal tools commit. Actual Git parents/trees, signatures, exact native three-file blobs/modes and research-only path sets are checked. Signed fix137 ancestry remains mandatory. The native receipt must attest exact remaining-diff and full-working-body preservation.

Acceptance schema follows fix137: status READY_FOR_STANDALONE_SIGNED_COMMIT, fix138, native_paths, validated_patch, phase_order, phase_counts, observed_repairs, unchanged_controls, existing_regressions, terminal_review, canonical_lean_increment=0 and native_refinement_proved=false. The patch must equal the v1 draft entry's repair-v2 reference. Terminal review is a path/SHA reference. Receipts use commit,parent,tree,signature_verified and native paths or research files. Actual assessment rows supply phase counts, repaired/unchanged counts,73 target identities and329 regression identities plus6 reftests; they must agree with acceptance. The candidate source and binary hashes must agree with the supplied current epoch. The fixed capsule and proposal manifests/payloads authenticate.

The script requires the exact five current preimages captured in immutable ledger-plan-v1. A preceding research commit alone does not invalidate this, but any intervening ledger-body edit makes it fail closed before writing. Request a reviewed/versioned preimage refresh in that case; never bypass the check or copy stale whole files over newer history.

Full preservation runs before any publication, again immediately before publication, and after all five ledger writes with only those pins refreshed. Root/nested index entries/flags and raw index bytes remain unchanged. All old queue/group entries, held120, registered-number lead, fix137 record, and canonical checkpoints are preserved. It derives137 accepted/committed,138 tracked, Attributes18 from current136/137/17 and requires no duplicate138. The current All135 summary is corrected exactly once in each document; historical count text is untouched.

Only after pre/post checks pass does it replace CURRENT-EPOCH.json and write RAW-LEDGER-UPDATE.json. Exact ledger and epoch preimages and input pins are saved under raw-ledger-preimages first. If a filesystem or preservation failure interrupts publication, stop and inspect those saved records; this script does not silently roll back or retry partial writes. Existing output paths prevent accidental replay.

Validation performed here is Python syntax and static matching of every current Markdown replacement anchor against real captured preimages, including plan status/execution wording and current count rows. No live update, candidate result, signed future receipt, acceptance or new count has been fabricated. EOF parsing remains outside the Lean guard proof boundary. ledger-plan-v1 and its draft entry remain immutable.
