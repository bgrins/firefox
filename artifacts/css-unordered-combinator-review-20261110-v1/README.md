# Independent replay

Run from the Firefox root:

```sh
python3 -I -B artifacts/css-unordered-combinator-20261110-v1/replay.py --lean artifacts/stylo-bloom-tools/lean-4.35.0-rc4-darwin_aarch64/bin/lean --out /tmp/css-unordered-independent-replay
python3 -I -B artifacts/css-unordered-combinator-review-20261110-v1/independent.py
```

The first output directory must not exist. The second command authenticates frozen author inventories, compares local preserved origins, checks an independent category oracle and builds/audits nine review proofs in disposable scratch. Its logs are review-owned. REPORT.md records scope and limitations; RECEIPT-AUDIT.json records independent command-log/type checks.
