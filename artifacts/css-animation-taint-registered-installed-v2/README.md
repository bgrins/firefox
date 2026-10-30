# Disabled registered-scope V2 collector

The run.py, report.js and check.py bodies are byte-identical to registered-installed-v1. Only fixture/resource references, separate runtime-2 output paths, predecessor references and the disabled execution gate change. The installed application/inventory pins, watchdog, profile/process cleanup, nonce transport and raw-versus-policy reporting are unchanged.

The new fixture adds hidden to the diagnostic pre, preserving all sampling and assertions. V1 Firefox transport/cleanup completed but its four-mode observation did not: literal timed out after its initial phase (harness2). This successor neither rewrites that result nor reruns its output directory. Offscreen iframe throttling from visible accumulated diagnostics is a hypothesis, not established cause. Chrome V1 was not executed.

After root review and activation, run serially:

```
python3 -I -S -B artifacts/css-animation-taint-registered-installed-v2/run.py --browser firefox --run
python3 -I -S -B artifacts/css-animation-taint-registered-installed-v2/run.py --browser chrome --run
```

No timeout increase, profile preference, native source/app install, Git/index operation, or browser launch is performed by this preparation. Actual application/inventory checks remain in root execution. Preserve WPT/harness outcomes, raw trajectories, incomplete record status and separate calibration/control/policy comparisons exactly as before.
