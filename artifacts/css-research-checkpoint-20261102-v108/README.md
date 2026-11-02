# V108 — disabled retry of the uncommitted V107 checkpoint

V107 signing failed in 21127/0ecc30/f3c90c with outer exit 1 and Git exit 128: 1Password reported “failed to fill whole buffer.” No commit was created. Root verified unchanged V106 HEAD 70d9, clean tracked tree/index, unchanged refreshed epoch b780, all 335 selected payloads intact and the transition lock absent. The failed owner, signing log, actual terminal and disabled preimages are preserved without editing V107.

This retry selects the exact same 335 completed records plus the closed V107 attempt and this small successor. Signed V106 remains the prior receipt; the actual completed raw refresh and V107 full current capture are reused without relabeling them as fresh V108 observations. The production signer changes only its disabled gate and V108 labels/temp prefix; its signing subject and full preservation/signature/canonical tail are unchanged. Root must pass the usual live `--check` before activation, so any intervening state drift rejects the retry.

The research outcome remains unchanged: original 6 PASS/15 FAIL, candidate 17 PASS followed by a typed-attribute CRASH before any callback; candidate observation incomplete, independently restored, backup removed. The catalogue remains 156. All 21 remaining WPT research copies were verified against committed recovery. No new browser/native/research work or acceptance is performed here.

Execution is disabled. Do not retry signing until the user indicates 1Password is ready. Root alone runs `commit.py --check`, preserves disabled preimages, enables the single EXECUTION_ENABLED literal, reseals FILES, then runs `commit.py --run`; neither command takes a manifest argument.
