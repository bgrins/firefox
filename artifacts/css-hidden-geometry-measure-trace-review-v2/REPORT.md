# Independent hidden-flex four-variant runtime review

## Verdict

Accept the bounded diagnostic findings and restoration evidence. Authenticate producer FILES `096d8b67f72453aea8ac9a843cdaf538fb7715c5320344f28073dd522621531d`: all 81 payloads match. Independent `recount.py` reads raw results, reconstructs exact configuration/stage rosters and expected geometry, joins actual variant source hashes and records native log excerpts. It does not execute a browser, build, compiler or Git command.

| Variant | Fixed-size failures /160 | Shrink/descendant failures /240 |
|---|---:|---:|
| Baseline with logging | 32 | 12 |
| Containing-block key omitted | 0 | 12 |
| Item dirty on hidden measurement miss | 0 | 4 |
| Principal subtrees dirty at skipped child layout | 0 | 0 |

All eight result objects have stable before/after pins, complete closed rosters and identical first/second/third reads. Every shrink visible-reference calibration passes. Four variants therefore supply 1,600 stage records, with three repeated target reads per stage; these are correlated finite observations, not 4,800 independent tests. The final candidate improves 44 failing stage outcomes over baseline and satisfies all 400 stage oracles in these two fixtures.

## Observed native path

Baseline fixed-size log contains a same-process/same-frame sequence: cached containing-block size changes from `(19200,1073741823)` to `(19200,0)` app units, while computed size stays `(1440,1920)`. The cache is rejected. The immediately paired measurement logs show `dirty=0 hidden=1 size=1440,1920 next=0`, then `dirty=0 hidden=1 size=0,0 output-b=0`. These are actual log values, not a guessed 32px containing-block size. Source review identifies this as the temporary measurement/FinishReflowChild path.

The shrink log provides a separate miss: containing-block size remains `(6000,3840)`, but computed width changes from 6000 to 3000 app units. Clean hidden measurement again commits zero. This route does not depend on the added containing-block key field, consistent with the key-omitted variant retaining all 12 shrink failures and with the separate installed-release observations.

The partial repair's paired logs change the after-measurement dirty bit to 1 while retaining the zero temporary size. Its remaining four failures are all hidden nested descendants at insertion: append/prepend × bounding/offset, reporting 100×32 instead of 50×32. Thus making only the flex item dirty is observably insufficient for this descendant query matrix.

The skipped-children variant still shows the original clean-zero measurement sequence before its later branch operation. Both complete browser matrices nevertheless pass. This supports fixing forced-layout admission at skipped child layout rather than requiring measurement itself to return final geometry. The trace does not directly log every subsequent dirty propagation or query-to-frame association; source semantics and controlled variant/outcome comparison provide that link. Retained excerpts identify process/frame and log location, without pretending the unlabelled aggregate native log is a per-DOM-case lifecycle trace.

## Source/build/restoration

The reviewed four-phase driver and INPUTS retain the previously approved hashes. Every run's flex source matches that phase's retained candidate; the remaining 24 native source hashes match common inputs. Test HTML/JS, runner, INPUTS, executable and XUL are stable across each individual browser execution. Five build operations (four variants plus restoration) return zero; each retained build log reports success. Build-monitor export exceptions and warnings remain in the original logs, rather than being erased. Browser exit −15 is intentional runner termination after complete result receipt.

Historical BEFORE equals FINAL for all 25 native files, HEAD and complete staged-index hashes; recovery errors are empty and STATE is terminal. No live comparison is needed while subsequent work may legitimately own the tree. A successful restoration rebuild is evidenced; identical pre/post rebuilt XUL bytes are not claimed. The independent review leaves the producer capsule and production files untouched.

## Landing and remaining gates

The containing-block key is needed for its caption-cache correctness case, but this experiment shows that it exposes additional fixed-size failures through an older skipped-layout protocol defect. Keeping fix101 on hold until repair/dependency resolution is supported. Removing the key is not a final repair. Conversely, the successful principal-subtree candidate has not yet been tested standalone without fix101; its release-reproduced shrink cases are the appropriate independent regression witness for that future check.

This is an instrumented shared-tree diagnostic, not final native acceptance, an uninstrumented landing WPT run, a performance result or full cache/lifetime proof. Required next gates remain: minimal source/package review, dedicated WPT with relevant controls, standalone dependency check, and residual tests for positions, already-dirty ancestors with clean descendants, nested visibility, anonymous frames, continuations and out-of-flow ownership. Existing direct-item formal reasoning must not be advertised as proof of the broader principal-subtree candidate. No new security conclusion follows.
