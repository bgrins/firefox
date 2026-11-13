Preparation only; no execution is authorized by this file. Root must supply an external authorization bound to this V2 FILES.json and a fresh output directory. AUTHORIZATION-TEMPLATE.json remains false and sealed. Resource/command fields remain commands=2, seconds_per_command=180, rss_bytes=2147483648 and stdout_stderr_bytes_per_command=67108864.

```sh
python3 -B artifacts/css-grid-baseline-grid-bundle-abi-preparation-20261112-v2/run.py --authorization /absolute/root-owned/authorization.json --out /absolute/fresh/execution-directory
```

If the host's Python isolation removes the script directory from imports, root may use its previously reviewed runpy bootstrap adding only this pinned preparation directory. Record the exact outer invocation; do not alter run.py or Clang requests. Retain terminal receipt, RESULT.json, both COMMAND/PID receipts, complete outputs, emitted dependency files and authenticated dependency maps. No follow-up compiler is implicitly authorized after a refusal.
