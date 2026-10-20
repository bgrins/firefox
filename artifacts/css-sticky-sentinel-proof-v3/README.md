# Geometric sentinel correction v3

Read REPORT.md, SCOPE.md and capsule/SOURCE-ROLE-v3.md. Independent acceptance is required. This artifact preserves the complete v2 under predecessor-v2 and the independent R1/R2 HOLD under review-v2.

The source-only executable is capsule/check.py. Authenticate the supplied external FILES/FREEZE/checker pins before importing or executing it. The inner manifest hash is recorded in CAPSULE-IDENTITY.json. Then run:

```
python3 -I -S capsule/check.py --manifest-sha HASH --output NEW_EXTERNAL_DIRECTORY
```

The checker pins the existing Lean installation and native tool/header closure and rebuilds all selected proof/native inputs. It does not rebuild Lean or verify compiler correctness. No browser or Gecko build is needed. The native source is the original geometric-sentinel candidate and intentionally excludes later inset-alias/negative-inset repairs.

`relocate.py --output NEW_EXTERNAL_DIRECTORY` makes an authenticated manifest-only source copy and replays there. `guard_capsule.py --output NEW_DIRECTORY`, `challenge_axioms.py --output NEW_DIRECTORY`, and `challenge_joined_rows.py --receipts REPLAY/joined --output NEW_DIRECTORY` exercise independent failure controls. Keep their outputs outside capsule. Completed compiler products may be removed only after retaining terminal receipts.

V3-DELTA.json identifies the exact source changes: all original native inputs, provider facade/extraction, original 59 declarations, calibration decoder, prior mutations and tool inventories remain unchanged. New modules derive finite indexed traversal/reference correspondence and executed machine-domain joins. The unchanged historical sources and failed development receipts are evidence, not alternative current acceptance gates.
