# Indexed-C comparison with 1024-update batches

Prepared only: no native/browser execution or live/index changes. This private wrapper uses the separate `css-revert-rule-long-cost-benchmark-v1/benchmark.html` unchanged. It fixes counts 0,32,64,128,256; seven samples; 1024 updates/sample; four warmups. That gives fifteen rows, 105 samples and 107520 measured updates per repetition. No-rule zero cases and literal/Layer controls are retained, with the same rotating row order and exact value checks.

Baseline source role is exact committed A+B+D. Candidate is exact A+B+D+indexed C: cascade SHA256 `b454e10310175f3c41bbe8cadde6fb8d0b12ee3e1bb900f91422cd44cad453f3`, required stylist `fd5ded7d96e15b16caacd03bc758da255333bdbed9b99bb4bc65bc6a1900b9b3`, and unchanged A+B+D applicable-declarations. `SOURCE-ROLES.json` retains all six baseline/candidate hashes from the reviewed indexed short-batch package.

Public interface is unchanged: `run(root, output, pins, cancelled)` and `active_processes()`. Fresh pins include execution_enabled, source_role, binary, build_revision, harness_revision and source/application SHA256 map. `pins['repetitions']` defaults to two and accepts one or two. Each repetition uses a separate WPT process/profile; a failed or incomplete first run stops the second. Required RESULT fields remain complete_observation, safe_to_continue, supplemental_audit_passed and all_pass, plus repetitions and report_paths. all_pass means correctness/report integrity, never a timing threshold.

CLI: `python3 -I -S -B artifacts/css-revert-rule-indexed-long-cost-wpt-v1/run.py --pins FRESH-PINS.json --output artifacts/NEW-OUTPUT --repetitions 1 --execute`. Root owns execution, builds and restoration. Keep the same batch length and preferences across compared roles.

The exact benchmark is in a private same-origin iframe. The wrapper retains the forty-second completion deadline, WPT long timeout and 180-second outer deadline. The benchmark retains its one-second/sample and thirty-second/run guards. Timing exhaustion is an incomplete measurement, not a conformance bug. These are safety/completion limits, not a speed-acceptance threshold.

Reports use prefix `CSS_ROLLBACK_LONG_COST_V1 ` and version `cold-c-chain-long-v1`. The assessor requires seven 1024-update samples per row, 7168 measured writes/reads/checks per row, exact CSS/mode/count coverage, no mismatches and complete report capture. Units divide elapsed time by 1024; the required total is 107520. Chunk uniqueness/completeness, finite timing data, source/application/run_info bindings, raw fault checks, cancellation, preservation and owned-group cleanup remain inherited from the reviewed runner. Full raw reports and timing summaries remain under each repeat directory.

Explicit preferences remain layout.css.revert-rule.enabled=true, dom.window.dump.enabled=true and privacy.reduceTimerPrecision=false. This local measurement configuration is not a release-default claim. Finite zero timings remain accepted; avoid ratios with zero denominators.

`CHECK.json` records syntax compilation, inert callback registration, manifest/config checks and synthetic report validation only. None executes the benchmark or proves its native timing/path. Existing short fixtures/packages remain unchanged. `FILES.json` seals the new package.
