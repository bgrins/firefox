# Public-history producer replay receipts

The source capsule is `css-parser-public-history-admission-v1`; authoritative external hashes are in `SOURCE-PINS.json`. It was authenticated, copied from its exact closed manifest to a clean relocated directory, and replayed with pinned Lean/Rust tools. The source capsule remains unchanged.

`replay/REPLAY.json` records all successful source-only stages. This receipt package retains complete proof audit and mutation diagnostics, native commands/results and independent Lean output; generated binaries and copied dependency trees are excluded.

`integrity/CHECK.json` retains eight rejected challenges. Each failed before output creation and no shadow module executed. The duplicate-key test adjusted its local internal manifest seal solely to reach the JSON uniqueness guard; independently pinned parent hashes would reject that tampering earlier.

These are producer receipts, not independent review or whole native parser verification. Source/model premises remain in the source capsule's REPORT and SOURCE-ADMISSION.
