# CSS verification continuation 172

Continue the full objective and [continuation171](../css-continuation-roadmap-20261103-v171/PLAN.md). The previous goal turn made progress by launching native validation. This turn completed the actual build, 61 browser assertions, independent restoration audit and exact baseline comparison. HEAD remains e86b64866cdc with 157 committed fixes. The font-unit repair is validated but uncommitted; the two earlier validated taint repairs retain publication priority.

## Active root operation

Raw-index refresh **34832b / session70533** is running through `css-keyframe-font-unit-raw-index-refresh-v2/run.py --run`. Active FILES is `c5723da7db5b5efcbeb4e005f86185f9fee3f416011fd0be7d7f27b3276868ac`. Log: `css-keyframe-font-unit-raw-index-refresh-root-run-v2.log`. Output, if written: `css-keyframe-font-unit-raw-index-refresh-runtime-1`. Poll the same handle; no terminal has been observed. Root has no active build, browser, audit or signer process.

Root cf6b0e bound the actual native/audit/runtime/raw records into disabled successor `7f09dbb024d6d137bceae39ab3e71d49d8fe2d9706e59e050c517126504b62fa`. Its run.py (`01316229473cc3ebce32ce00286d8b27a3a31f16c3b50fa89424df1ddf90070e`) is byte-identical to reviewed preparation 1fb09b44. Root 07efa7 preserved disabled preimages in `css-keyframe-font-unit-raw-index-refresh-root-activation-v2`, flipped only execution_enabled, and authenticated all 132 references. The unchanged --run validates saved evidence before live operations and again before writing; a separate duplicate --check was omitted without removing a guard.

The intended one-field change is canonical raw083f1ae2 to actual `c1d5743411f801baba1c8202ed20f829ca80fcee9e93d37450299c6f5fa86fe8`. Semantic index, source, application and other controls must remain identical. Signed native authority085f/e86 and prior bridge59213ad4/epochf83 remain bound. Do not invent a new epoch or change HEAD while this operation runs.

## Completed native evidence

Native owner **4fdd14 / session41426 / 47a62c / exit0**, outer PID/PGID64247, completed with active owner manifest b8369329. Build binaries -j2 succeeded in 44.50 seconds, compiling Stylo/geckoservo/gkrust and linking Gecko. Candidate build ID was **20261103012417**, revision e86. Candidate sources were data.rs17aaffd1 and traversal.rs402165f9. Nonfatal Mach export-monitor KeyError traces remain in the successful build log.

All 14 focused assertions and 47 controls passed, with five OK page endings. The owner restored original data.rs6a7df6b0/inode[16777230,243853681], traversal.rs73692012/inode[16777230,243853843], application/extras and semantic index/flags/controls. It removed its verified 1,008,605,176-byte backup. Root a22d87 independently rechecked source hashes/inodes and backup/lock absence.

Native RESULT: `56ca5230502100b2d334b2312dfba57e668db06ff148a346c180fd833d9c75ba`.
ROOT-OWNER-TERMINAL: `3e120379bc270d46ea9792f9caf0ff6ee0f703f40f9e591dd29bb6905fa34423`.

Independent audit **9246dc / session59364 / 883131 / exit0** verified live source/application/binary/index/control/flag restoration, raw replay, process and temporary-root absence. Audit v2 FILES is `d0bf72465e1964a083afc85bf1b20eb86865cb070de2c7bc1ddfe25e5e5964e1`; audit.py022d10b9 is byte-identical to reviewed v1. ROOT-LIVE-RESTORATION is `5d358e12c1185b62921bf52b2b469d94c143100a51231759ec64ea1402baa3bb`; ROOT-AUDIT-TERMINAL is `dc6339174bc95ba844877dbb870711ae366e73e8b2d00d27745f71ed5a4219c2`. Initial root preparation2f0735 wrote the correct owner terminal then rejected the old audit manifest's string-value format before creating v2; corrected authentication9fcfe5 preserved exact hashes. This is documented in the audit README.

Root e4fde8 froze `css-keyframe-font-unit-candidate-browser-runtime-v1`: FILES `4e5fdea12bdaefcf9aa4b887b6ac0a783ac5f93e4a04bf2b424bf8cd5d23bbc4`, 76 regular payloads and exactly two verified tests/tools symlinks to the repository WPT tools. No backup is included.

Actual comparison **eaa298 / exit0**, frozen b796e6 as `css-keyframe-font-unit-native61-outcome-v2`, FILES `b00461302b589df509722c0a834ea8ed9ef46de4006c561996f78301378a681c`: exactly **12 FAIL-to-PASS changes**, all **49 prior PASS and five ending full signatures unchanged**, all **61 candidate PASS**. compare.py542b3ffb is unchanged; root explicitly joined terminal.result_sha256 before binding. Candidate build RESULT is `8aca3af99e4f8212711baad2409e0e0905ff3aec06d8f28c6755df6a0184595b`. This does not increment the committed-fix count.

## Publication next

After the raw-refresh terminal, independently verify its one-field canonical change, PRE=POST, unchanged controls and absent lock, then freeze its runtime. Bind V123 refresh_prefix to existing combined59213 and refresh_binding to the actual new result; set epoch_sha256 from the real EPOCH. The existing capture_current.py runs without arguments and exclusively creates `css-research-checkpoint-20261103-v123-current.json`. Keep bindings stable while it runs. Do not run check.py in the intermediate state: its pending branch requires null epoch/refresh.

After actual capture, bind its hash/controls, clear pending_current_admission, and add completed receipts/capture/log/roadmap and required artifact dependencies to selection/references/complete-package map. Keep self files out of SELECTION because commit.py adds them. Agent's read-only schema review93ac74/661ef1/98aee6 confirms no new checkpoint tooling is needed. Complete final checks and one normal configured signing attempt, preserving failed V122 and all failed attempts.

Then publish typed recascade source plus four-case WPT; small rebased-publisher research; selected fallback source plus 28-case WPT. The newly validated font-unit fix follows with its own source plus WPT. Remaining root-self, cancellation, parent-variation and earlier formal milestones stay active.

## Separate memo prototype

Root836eb1 authenticated/read readset-review4722c964. Rootf0be39 reviewed the implementation, and9b1223 reviewed final seed fixd692abf3947e9ee735bf3ec434077353c3d2aeefdaae43725c276ed885661d83. Independent review cleared one saved-only replay, without live deployment clearance.

Actual saved-only110961/session10379/7fd323/exit1 failed closed after 3.10 seconds on an unlisted argparse import in an authenticated historical helper. saved-run1/log/terminal/attempted inputs are preserved. Partial cache hits are not a completed replay or speedup result. Root authorized only explicit argparse/configparser preloads after pinning helper87f49b75; memo code stayed unchanged. Updated inventory has 28 sources/17 modules; focused fixture4a78db/exit0 gives 12 positives and 18 rejections.

Independent reviewer33f01e cleared that exact two-import delta. Root3aa1b8 read PRELOAD-RETRY.patch and authorized a second saved-only replay in fresh saved-run2. Agent typed_demand_review owns this task and must report its actual handle/result. Deployment remains false, historical/live owner/source files remain untouched, and unsupported access must fail closed. The taint commit workflow does not wait for this prototype.
