Preparation corrections, before execution:

- Root caught that copied test_run("candidate") would collide with candidate/ source snapshots. The runtime output role was changed to standalone/ throughout; candidate/ remains source input only.
- The first static oracle-manifest authentication treated its older `{files: [{path, sha256, bytes}]}` schema as a flat map and stopped at roster validation. The corrected preparation explicitly decodes the old schema and authenticates every listed payload. No INPUTS or runtime result was produced by that failed attempt.
- Proposal-v4's original DOMRect is already fix102. The temporary pre102 role was obtained independently from the specified Git parent and checked against the retained historical integer-only source and runtime receipt.
