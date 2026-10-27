Root-only final checker for readiness comparison session20804. Run only after the owning execution handle reports terminal exit0:

    python3 -I -S artifacts/css-svg-length-readiness-final-check-v1/check.py --session-exit 0

The checker authenticates the activated comparison draft/references, requires terminal restored state with three successful builds, lint0, no failure/recovery errors, and exact before/final equality. It independently reparses both raw51-case runs, requires seven complete harnesses each, exact16 baseline failure identities/diagnostics and candidate51PASS, rejects infrastructure faults, verifies RUN/cleanup/build/source/binary/resource joins, and checks the exact comparison receipt.

It checks all53 live source guards,390 resources,30 saved originals and30 modified-native paths, all925 staged blob payloads plus index/HEAD fingerprints, seven installed WPT hashes/inodes, existing-test ownership, absence of the owned WPT and source temporaries, and actual rebuilt binary hashes. The final role map is recomputed exactly. No native,index,browser,build or runtime-file mutation occurs. The sole execution output is a new ROOT-FINAL-CHECK.json in this checker directory; root may copy that receipt into the runtime before sealing it. Output creation is exclusive.

Session termination is supplied by root from the execution handle; the checker does not inspect an external tool session or prove arbitrary system process quiescence. It verifies retained WPT cleanup receipts and actual terminal/restoration evidence. This is restoration verification, not acceptance or installation activation.

STATIC-CHECK records syntax validation and independent read-only replay of the completed phase raw files (35PASS16FAIL then51PASS), before restoration completion. It does not claim that the live restoration checker has run. The helper imports are transitively pinned by the authenticated activated draft's REFERENCES.json. No new framework or copied evidence tree is introduced.
