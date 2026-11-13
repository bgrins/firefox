# Source-only replay

From the repository root, choose a fresh output directory:

```sh
python3 -I -B artifacts/css-flex-total-violation-caller-proof-20261111-v1/check.py --out artifacts/css-flex-total-violation-caller-proof-20261111-v1/independent-replay
```

The checker uses the authenticated local Lean 4.35.0-rc4 binary and Std inventory, copies only this capsule's Lean sources, and compiles serially with one thread, 1 GiB, and 180 seconds per module. It reauthenticates source/origin/tool inputs after all controls. It checks 232 exact ordered axiom reports, seven retained executable-control lines, the finite 57-seed diagnostic, and six normal semantic refusals with exit1 and the expected single false-proposition diagnostic. Each worker has an owned process group; scratch removal is gated on observed group absence. Inspection/launch/signaling failures retain uncertain scratch. Failed development receipts remain separate from final acceptance.

The `--modules` option is development-only and deliberately does not claim the full audit/refusal gate. Root independent replay output should be separately owned and excluded from the author inventory.
