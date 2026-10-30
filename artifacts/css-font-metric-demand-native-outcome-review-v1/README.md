# Published native font-metric baseline

The fresh published-source build records **3 PASS, 10 FAIL, 1 OK** for the exact 13-case fixture. Independent saved replay checks the roster, all 40 phase observations carried by the ten failure messages, and their font-field, em-size and distinct-metric controls. There are **20 metric mismatches**. Passing callbacks do not archive phase values.

Twelve callback signatures (test/name/status/message) match installed Firefox 158 exactly. The typed-attribute callback remains FAIL, but changes from release's constant `8px` to `20px, 20px, 30px, 30px`. Its normal-weight phases now match; heavier-weight phases still use the earlier metric instead of `11.0167px` and `16.5167px`. The other failures retain stale metrics for weight, style, stretch, size-adjust, orientation and alias paths.

This distinguishes the release-only early-size symptom from the metric ordering failures still present in the published branch. The accepted resolved-attribute-unit work is a plausible explanation for the size improvement, not a bisected causal attribution. These observations do not establish a new bug count or accept a native repair.

Saved build and WPT receipts join published provider `bb13b61a`, cascade `5b7204f8` and registered-value `6624c2a5`, build/harness revision `a1e0ffba3651cf27853c33d22bb7b1b5368f658f`, BuildID `20261030123747`, and identical build/lane binary pins. The build exited zero; the WPT process exited one because failures were retained. Exact staged fixture, font and harness hashes are checked. This was an original-only build, with no candidate overlay. The release and local Nightly profiles are not assumed to have identical effective preferences; equal outcomes are observations across those recorded environments.

Owner terminal `80766 / c53f82 / a2c1fe / 0` authenticates its result and reports successful restoration, unchanged controls and empty staging. This package performs saved-evidence review only: it does not independently inspect the restored app, sources, processes, index or filesystem. Any separate root live audit has its own authority and receipt.

`check.py` is a bounded adaptation of the preceding release outcome checker. It reads saved artifacts and writes only this package's observations and reference pins. `REFERENCES.json` identifies the exact evidence; `OBSERVATIONS.json` retains full failure data and the owner result. No browser, build, Git or live restoration checks were run by this reviewer.
