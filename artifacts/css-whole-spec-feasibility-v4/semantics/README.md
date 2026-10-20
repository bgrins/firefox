# V4 semantics research

Read [REPORT.md](REPORT.md). This research adds a kernel-checked generic dependency-reading interface to the v3 architecture; two constructed clients exercise phase and epoch distinctions. It does **not** prove CSS sizing, animation, or native conformance.

- `prototype/Protocol.lean`: typed requests, reply-dependent plans, actual-footprint preservation and sequential composition.
- `prototype/Clients.lean`: sizing and animation examples, deliberate provider substitutions, absent-result dependency and same-episode coherence.
- `INTERFACES.json`: three proposed interfaces for the inventory workstream, all marked proposed.
- `evidence/`: final compilation/axiom/execution receipts; `prototype/*draft.log` retains an earlier IO elaboration failure.
- `spec/`: six current primary sources and verified anchors.
- `LOCAL.json`, `prior/`: exact prior report/library context.

Verify research integrity with `python3 -I -S check.py`. To replay, supply a **new** output directory and the Lean executable recorded in `evidence/REPLAY.json`:

```
python3 -I -S replay.py --output /private/tmp/css-v4-semantics-replay-UNIQUE
```

The replay compares all 13 exact axiom reports and four retained output traces. Golden traces are regression receipts; the phase/epoch/absence/coherence statements are separately kernel-checked. The Lean executable is recorded, but the entire installed standard library/runtime is not independently authenticated by this lightweight research runner. No claim of the earlier production proof-capsule guard suite is made. `check.py` is an integrity checker, not a proof of model faithfulness. The uncompiled host/episode sketches in REPORT remain proposals.
