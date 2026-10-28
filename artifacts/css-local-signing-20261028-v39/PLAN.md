# Root signing sequence

Run init.py, then the unchanged commit.py with research-selection.json, validation-selection.json and native-selection.json in that order. Each command must finish successfully before the next.

After the exact two-path native receipt, render the reviewed all-work readout for v39, review its output and seal it before finish.py. finish.py verifies the actual three signed receipts, readout and acceptance, publishes four owned ledger/roadmap documents, signs the checkpoint and synchronizes the canonical epoch. No source, build or browser action is part of this sequence. Preserve prior v38 final receipts and actual failed and successful preparation evidence.
