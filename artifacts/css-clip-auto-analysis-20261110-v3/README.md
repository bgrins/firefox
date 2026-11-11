# Corrected clip result comparison

This is an analysis-only successor to the frozen v2 comparator. It does not
replace the completed experiment, rerun Firefox, or provide a new native runner.
The original raw logs and receipts remain unchanged.

Result keys now include the record kind. A null-named first Mochitest callback
and its test harness result therefore have distinct identities. Duplicate keys
within either kind are rejected instead of overwritten. The clip preservation
gate also compares Mochitest assertion messages by test, name and occurrence.
It continues to allow exactly the four specified CSS FAIL-to-PASS changes and
requires identical SVG observations. WPT failure messages remain outside this
comparison because the intended improvements change their presence.

The synthetic Mochitest controls now use the actual protocol's null callback
names and repeated messages. All 25 inherited parser controls pass. Fresh
analysis of the retained raw logs reproduces their original parsed receipts and
compares all 5,116 callback/harness rows, with exactly four improvements and 12
unchanged SVG observations. Fourteen additional controls change each page's
first callback status, remove that callback, change its label, or duplicate a
parsed callback/harness record. The frozen comparator accepts each mutation;
the corrected one rejects each. These controls test the comparator directly;
the runtime parser and command exit checks remain separate defenses.

Run:

```sh
python3 -I -B check.py --evidence ../css-clip-auto-runtime-20261110-v2 --out /new/report/path
```

`SOURCE-ONLY.json` pins executable inputs. `RAW-INPUTS.json` pins six retained
raw/parsed evidence files. `ORIGINS.json` binds the original four inputs to signed
research commit `302fe2b5ba00`; `analysis.patch` shows the correction. No frozen
v2 input is modified. The broader trace parser remains specific to this clip
experiment; future native experiments must adopt the corrected key policy and
their own expected result inventory before running.

This is executable validation tooling, not a Lean theorem, another browser fix,
or evidence of additional CSS specification coverage.
