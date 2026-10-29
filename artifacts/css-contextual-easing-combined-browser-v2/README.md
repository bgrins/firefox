# Combined315 fresh baseline

Root-authorized baseline successor of the sealed disabled v1 capsule. Baseline execution is enabled; candidate execution remains disabled. Both baseline bindings remain null until fresh original evidence and an actual root-reported terminal can be bound in a separately reviewed candidate successor.

All executable bodies, the assessor, source roles and WPT policy are byte-identical to v1. The only policy changes enable baseline execution and authenticate the v1 manifest. The exact 315 callbacks across 22 pages, 41 targets, 274 strict controls, 296 control/ending signatures and original-PASS preservation remain unchanged. The original must complete without any assumed FAIL count. Resource gates remain 27 GiB after backup, 15 GiB running stop, 1800-second build and 900-second WPT deadlines. Full input, preservation, diagnostic and proof boundaries remain documented in the authenticated v1 package.

Root reported successful v1 static check 012a64/0 and live guard session 76185 terminal 824936/0 after review 97184e. AUTHORIZATION.json records this reported provenance; CHECK.json records the exact successor delta. Preparation did not run an owner, browser or build.

Root can authenticate with `GIT_OPTIONAL_LOCKS=0 python3 -I -S -B artifacts/css-contextual-easing-combined-browser-v2/baseline.py --check <FILES-SHA256>`, then execute the same command with `--run`. The baseline runs the existing restored application without a build and writes fresh runtime evidence under `artifacts/css-contextual-easing-combined-browser-runtime-1`. Candidate execution rejects this capsule. No native acceptance, new fix ID, proof discovery or coverage increment follows from preparation or baseline completion.
