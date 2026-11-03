# Post-candidate raw-index observation refresh

Disabled preparation for root execution after the standalone attr-fallback candidate and the two archived 28-case runs. It updates only `CURRENT-EPOCH.json`'s `raw_index_observation.current`. It does not install code, rebuild, launch a browser, stage files, sign, or change acceptance counts.

The actual candidate owner completed session 14079 (`b69f41` → `8d60f3`, exit 0), with a successful build and 24 PASS callbacks. Independent restoration session 23976 (`cac524` → `802c5e`, exit 0) verified the original source identity, application and extras, binaries, semantic index, flags, controls, process absence, temporary-root cleanup, and removed owned backup. The frozen runtime is `css-attr-fallback-candidate-browser-runtime-v2`, manifest `a704b5ebe807be5a79e4e73a22ebe4eccdef9b57406817451949d6faa0c4d218`.

The separately frozen archived runs both completed their lifecycle: original 17 PASS/11 FAIL with WPT exit 1; candidate 28 PASS with WPT exit 0. Both outer owners exited 0. Saved replay authenticates the exact 28 names, one page/start/ending, suite lifecycle, no crash, preserved archive inventories and staged inputs, and cleanup records. It reads only saved artifact files, not the physical archived applications. These validation results are supporting evidence; they do not replace the candidate owner's full-state restoration audit or constitute publication.

Authority remains the real signed native `e86b64866cdc5e2260ba9be08c45756fd96e21bb` receipt. The admitted rich capture already joins the executed previous raw refresh `542709d9…` to canonical epoch `dd386ebd…`. Failed V119 signing is not authority. The completed candidate observed raw index `5084fdf9…` → `83fb96b9…`; all other frozen snapshot fields match exactly.

`RUN-DELTA.patch` is relative to the executed integrated-pair raw refresh. Saved admission changes to the one-source, one-lane successful candidate and adds both archived validation records. `derive` and `admit_current_raw` are byte-identical. The transaction from control claims through write, verification, rollback, and lock removal is byte-identical except its operation label. The existing full live guards remain before publication. A new branch, after those guards and before output/lock creation, returns JSON with `updated:false` if the actual raw observation already equals the canonical observation. It creates no refresh runtime in that case. A differing current raw is admitted only with an identical semantic index and complete frozen post-snapshot projection; it need not equal the historical post-run raw bytes.

The root must review, run `--check`, activate only `POLICY.json.execution_enabled`, reseal the owner, and invoke `--run` with that active manifest hash. `check.py` is saved-only and requires the disabled policy. No live admission, canonical write, or refresh outcome has been performed for this package.

```
python3 -I -S -B artifacts/css-attr-fallback-postcandidate-raw-index-refresh-v1/run.py --check <FILES-sha256>
python3 -I -S -B artifacts/css-attr-fallback-postcandidate-raw-index-refresh-v1/run.py --run <active-FILES-sha256>
```

If a transition is needed, output is `artifacts/css-attr-fallback-postcandidate-raw-index-refresh-runtime-1`, retaining PRE, POST, exact old/new epoch, actual raw admission, and RESULT. PRE and POST must match in full. Any write-path failure restores the canonical preimage before releasing its owned lock. An already-current return must not be represented as a newly executed transition in V120.

Final saved check: `276f96` / session 94612 / `87b400`, exit 0. It authenticated the actual records, replayed all three WPT observations, passed 15 negative checks, checked both no-change/write-required branches, and compared the exact inherited transaction. Initial successful 13-negative receipt is preserved separately. No native/browser/archive/live-state check was run by this preparation.
