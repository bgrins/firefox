This disabled recipe runs the frozen animation-taint page and snapshot-preservation page against the restored local original Firefox build. It reuses the executed masked-nine original lifecycle and the same WPT, process cleanup, metadata and state-verification helpers. There is no build, source overlay, private record transport, Git mutation or canonical update.

The exact roster is six callbacks on two pages. The manifest is the disjoint union of the two sealed subset manifests, with identical shared harness entries. All HTML/JS resource bytes remain unchanged. Existing directory metadata and WPT profile preferences are inherited from the proven observer; this is a local branch baseline, not a stock-browser/default-preference claim. The original application build is 20ab7e with BuildID 20261029165244; its recorded restored entry/target identities are 279768875/279779416.

Admission authenticates the current restored-state/application receipt and the failed V82 signing preservation receipt. It does not require unrelated prior experiment outcomes. Runtime still verifies the exact three control hashes, historical original build/source and binary mapping, 29 accepted payload pins, application metadata and full current state before and after WPT. The existing owned process cleanup and 180-second watchdog are unchanged. Raw JSONL, assessment, browser exit, roster, PRE/POST and cleanup receipts are retained. Ordinary assertion FAIL is a complete observation; it is not converted into PASS. Setup exceptions, crashes or incomplete callbacks remain failures. Passing callbacks do not retain full diagnostic trajectories because the frozen fixtures have no private transport.

Root commands after saved review:

```
python3 -I -S -B artifacts/css-contextual-duration-taint-preservation-original-v1/run.py --check FILES_SHA256
```

For activation, preserve the disabled POLICY.json and FILES.json, set only execution_enabled=true and activation_pending=[], then reseal FILES.json. Root runs exactly once with that active digest:

```
python3 -I -S -B artifacts/css-contextual-duration-taint-preservation-original-v1/run.py --run ACTIVE_FILES_SHA256
```

The exclusive output is artifacts/css-contextual-duration-taint-preservation-original-runtime-1. No output directory is created by the saved check. Root should record the actual terminal, independently replay the exact six names/two endings and verify restoration before freezing observations. No baseline PASS count is assumed: animation-taint failures are evidence, not a reason to discard the run or rewrite its oracle.

The package includes the concise run/assessor deltas, current policy and static checker. The checker covers all-PASS, all-FAIL and mixed complete streams plus twelve malformed/incomplete/lineage failures. It authenticates exact fixture bodies, union manifest and resources without regenerating or linting sealed fixtures. No browser or full current-state guard ran during preparation.
