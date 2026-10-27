# Disabled quote ledger candidates

The five postimages in `preview/candidate/` are prospective only: fix 135, 134 committed/accepted fixes, held repair 120 excluded. They contain explicit pending commit/receipt tokens and MUST NOT be applied. No terminal outcome or signing is asserted by preparing them.

Category: Text and fonts (13 to 14). Tentative P3 visual correctness. Discovery is source audit plus browser reproduction; conditional Lean corroboration is separately qualified. Planned comparison fields are candidate/original/candidate 64 PASS, 52 PASS + 12 FAIL, 64 PASS, with 18 existing regressions unchanged (15 PASS, three expected FAIL). Final generation refuses different counts; a different actual result requires root review and a revised proposal, not relabeling observations.

The JSON preserves all prior fix entries and histories. GROUPS animation total is corrected from 14 to its existing 16 records without counting new animation work; tracked is recomputed from group totals (135 including the one held repair), correcting the old stale 132. Existing current-ledger pending count includes the held repair and is preserved; its excluding-holds value remains zero. Formal-library and provider-host checkpoints remain unchanged. Next work is real winning-provider integration, not another quote validation plan.

After terminal GO and both verified signed commits, root fills BINDING.template.json in a separate directory: ready/terminal_GO/signatures_verified true; full research/native hashes; authenticated terminal-review and signing-verification file references. These booleans are root adoption assertions, not an independent signature verifier. The helper authenticates reference bytes and validates the explicit outcome contract; root must confirm the referenced receipts actually cover these commits and this execution. No Git calls or live writes occur.

Run from the checkout:

```
python3 -I -S -B artifacts/css-quote-scope-append-ledger-proposal-v1/prepare.py --binding /absolute/path/BINDING.json --output artifacts/ABSENT-ROOT-REVIEW-DIRECTORY
```

The helper requires all five live preimages still match BEFORE-PINS, then writes only candidate files, a patch, binding and check in the absent artifact output directory. Root reviews/applies separately. It does not stage, commit or update ledgers. If signing changes ledger bodies, stop and rebase the proposal explicitly.

Validation: preview generation passed; five current live hashes stayed exact; all old fix entries and JSON history prefixes remained exact; README/PLAN historical sections remained exact. Eight synthetic negative controls reject disabled/unadopted/unsigned binding, malformed/equal hashes, wrong phase/regression counts and a bad receipt hash. Synthetic receipt data is not actual admission evidence. No browser, compiler, native or index actions were performed.
