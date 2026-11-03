# Direct native epoch equivalence for future diagnostic admission

This pure saved-data helper compares the actual original native publication epoch with the later trace-capture epoch. It is not an execution owner, a cache, a native-head adapter, a signature verifier, or permission to run diagnostics. No existing owner or live validator is changed.

`equivalence.verify_saved(repository_root)` reads seven explicitly pinned existing artifacts; it does not copy either 7,937,923-byte epoch. The original bytes are the first post-native refresh's `PRE-CURRENT-EPOCH.json`, whose SHA-256 is exactly the epoch digest in the actual capacity native `COMMIT-RESULT.json` (`085fcdc6…`). The original V115 capture was successfully executed even though the later V115 research signing failed. Its capture terminal binds that observation; it is not a signed V115 research receipt.

The current side uses the completed archive-refresh `EPOCH.json` (`e3b00d56…`) and actual trace capture (`da0e0cf7…`) with its terminal. No canonical file, source, app, index or process is inspected. The native publication runtime has no `POST.json`; the original observation is the V115 capture's `audit` snapshot under the original epoch (`8fecf2c4…`).

After authenticating exact file bytes, the helper joins the unchanged native receipt, both native HEADs, epoch-control digests, capture terminals, semantic root/nested indices, and each epoch's raw-index digest to its own snapshot. It compares the **entire epoch** after replacing only `/raw_index_observation/current`, and the **entire snapshot** after replacing only `/index/raw_index`. Other control hashes must remain identical. The permitted change is `2cef564f…` to `1dda5e97…`; nested raw index, pins, identities, counts, provenance and all other fields are not exempted.

Comparison uses canonical JSON serialization with `allow_nan=False`, not Python structural `==`: booleans, integers and floating-point numbers cannot compare equal by coercion. Parsing rejects duplicate keys, explicit nonfinite values and overflow to nonfinite floats. The input domain is authenticated JSON, not arbitrary Python objects. The private `_compare` function expects already authenticated decoded documents and is used directly only by tests to exercise deeper guards rather than repeatedly stop at the hash guard.

Run the read-only saved check with:

```sh
python3 -I -S -B artifacts/css-native-epoch-direct-equivalence-v1/check.py
```

It prints its result and never rewrites a sealed receipt. Controls separately cover exact byte-pin rejection, bad original/receipt/terminal/raw joins, changed non-exempt epoch/snapshot/control fields, source identity changes, boolean/integer/float substitutions and malformed JSON. No browser, native compile, historical semantic-admission replay or formal suite is run.

## Future integration obligations

This result can support replacing recursive raw-refresh-history replay **only for a separately reviewed future diagnostic admission**. It proves equality of these pinned saved states modulo the stated observation fields. It does not verify every intervening experiment's outcomes, restoration history, authorization, or publication acceptance. It is not a generalized bridge for arbitrary future epochs.

A future caller must still authenticate its complete source/build/fixture/helper input closure and expected native receipt; freshly verify signatures, ancestry, native parent and exact commit paths; and perform unchanged full current-state, source-hash/inode/HEAD-byte, app/binary/extra-resource, metadata, flag, control, absence, lock, process and resource checks. Additional sources absent from the canonical epoch still require their captured claims and HEAD-byte checks. It must join the fresh observation to this saved target and preserve all transition, restoration and independent archive-audit checks. Equality here cannot substitute for those live checks or infer them from a previous capture.

No live result is cached or returned. The returned object is labelled saved equivalence evidence, with live checks, diagnostic authorization, historical outcome verification and publication acceptance all explicitly false. The active trace run remains untouched.

## Saved result

Actual `2442a2/0` verified both whole-state equalities and 32 rejecting controls in about 0.85 seconds. `CHECK.log` is the unchanged printed result; `CHECK.json` records execution and review attribution. Peer `88ae5f/0963ca` independently read the helper/tests/scope and authenticated all seven inputs and both tested code hashes without rerunning the test. No native or live validation is claimed.
