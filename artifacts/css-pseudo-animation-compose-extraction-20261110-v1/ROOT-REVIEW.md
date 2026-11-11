# Root review and optimized native comparison

The formatted two-file composition extraction compiled successfully and preserved the exact results of the selected browser baseline. This is a tested prerequisite patch stored as research, not a delivered CSSOM bugfix or a completed debug gate.

| Run | Pages | Callbacks | PASS | FAIL | Page outcomes |
| --- | ---: | ---: | ---: | ---: | --- |
| Retained baseline | 29 | 258 | 230 | 28 | 24 OK, 5 reftest PASS |
| Built extraction | 29 | 258 | 230 | 28 | 24 OK, 5 reftest PASS |

Root independently parsed both raw logs and compared all 287 `(page, callback-or-harness)` keys and statuses: no additions, omissions or changes. Diagnostic messages were retained but not used as equality keys. The candidate XUL hash differs from the baseline and the candidate build receipt binds both edited source hashes. Build exit was zero. The known Mach monitor `KeyError: 'export'` appeared, but the build itself completed successfully; it was not treated as a source compiler failure or silently used to bypass compilation.

The 28 callback failures comprise seven retained-CSSOM controls, three underlying-value controls, seven target.html cases (including the separate placeholder expectation), eight tentative opacity-clamping cases and three iteration-composition cases. This comparison does not fix or independently establish those existing failures. The exact test selections and untouched metadata are documented in RUNNER.md.

Root reviewed the source change, then replayed check.py. The separately authenticated source review in ../css-pseudo-animation-compose-review-20261110-v1 found no blocking issue before runtime. Ordinary timing/null-progress handling, property iteration/skip order, segment selection and overflow bookkeeping are preserved. The stable-input/no-reentrant-mutation premise and valid nonempty segment-array preconditions remain explicit; compilation and tests do not prove those universal premises.

Root independently compared the final full application and all three extras against both pre-run snapshots, checked baseline native source/binary hashes, HEAD/index, tracked cleanliness and absence of temporary fixtures, metadata, lock and backups. ROOT-RESTORATION.json records these checks. Both owned application backups were removed after verification, as were redundant formatter output copies identical to the retained candidates. Build intermediates outside the application/extras are not claimed restored.

The optimized run covers the two pseudo fixtures, target.html, commitStyles.html, combining-effects and keyframe-effects. Debug assertions, broader CSS animation/transition suites, compositor/throttling/overflow integration and future CSSOM snapshot/recascade behavior remain outside this completed gate. Keep RUNTIME-GATE.md as the proposed fuller acceptance gate. Do not describe this extraction as a fix for bug 1615083, and do not land it alone as that fix: the final native repair must include the necessary source and WPT in its own self-contained commit.

Whitespace audit preserves the exact Searchfox receipts base-style-callback.txt and timing-callback.txt, unified-diff context prefixes in extraction.patch, and the frozen copied process.py (one historical blank EOF line). These four evidence inputs are excluded from the staged whitespace check; their hashes remain bound to the executed runtime inputs. Authored source and documentation pass the remaining check.
