# Tab-cache caller audit

Read `REPORT.md` for findings and open gates. This is a static evidence capsule, not a native or browser test result.

Replay from any directory with Python 3.9 or newer:

```
python3 -I -S -B /absolute/path/to/capsule/check.py --manifest-sha HANDOFF_SHA256
```

Use the manifest hash in the independent handoff. The checker authenticates all inputs before loading local code. No Gecko checkout, compiler, network, Lean, browser or build products are needed. The archived Node syntax receipt is not rerun by the checker.

The browser diagnostic is `mathml-cache-origin.html` plus `Ahem.ttf`; its twelve fixtures have not been executed by this worker. Root owns any browser run and source/binary binding. Read the MathML normative qualification before interpreting its output.
