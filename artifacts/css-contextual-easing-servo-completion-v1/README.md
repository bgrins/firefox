Both complete Servo style checks succeeded under the explicit
--force-warn missing_docs policy: baseline42.1256 seconds, candidate10.4996
seconds. Root observed session2951 terminal85dc63/0. Exact sources/dependencies
were preserved and all owned groups were absent. RESULT.json and PAYLOADS.json
bind actual runtime results, commands, tool versions, preservation receipts,
and the root terminal; RAW-LOGS.json hashes all five original output logs.

The warning audit retains every rendered compiler diagnostic and reconciles
all Cargo summaries, including separately reported duplicate warnings.
Baseline emitted11,978 diagnostics and candidate4,180. All4,180 candidate
diagnostics match baseline, including all3,671 style-library warnings. There
are no additional candidate diagnostics. The7,798 baseline-only diagnostics
belong entirely to compiler scopes absent from candidate output; raw totals
therefore cannot be compared without accounting for scope/cache reuse.

Matching normalizes only baseline/candidate workspace prefixes, location line
numbers, and their gutter indentation. Columns, full message text, notes,
markers and rendered snippets are retained. All23,876 displayed snippet lines
were checked against407 source files. Rustc truncated35 displayed lines; each
prefix was checked and the complete actual source-line hash retained. Paired
source lines and snippet hashes match exactly; no paired span line actually
shifted in these logs. No warning category besides missing_docs was observed.
The unused-getrandom-patch resolver message is identical and tracked separately.

This establishes warning equivalence, not warning cleanliness. Broad force-warn
enabled thousands of pre-existing documentation diagnostics, including ones
normally allowed. The known held-provider diagnostic is among them. The original
strict-lint baseline still has its preserved failure. No global lint cap,
bootstrap flag, native Rust edit, provider acceptance, candidate native
acceptance, clean-upstream claim, or runtime proof is implied.

Full source/span/snippet/diagnostic mappings and one-to-one candidate pairings
are compressed under local/ and hash-bound by WARNING-AUDIT.json. Keep these
local or select their hashes for compact checkpoints; do not copy large raw
logs or source bodies into the checkpoint. Four generated sources used by the
diagnostics are preserved through GENERATED-SOURCES.json. The5.4MB properties
body reuses the existing cleanup-v1 retained copy; only448,400 new bytes were
copied for the other three files. The audit no longer reads any runtime target.

Read-only reproduction, including every diagnostic pairing and retained source
check, remains possible after target cleanup:

```sh
python3 -I -S -B artifacts/css-contextual-easing-servo-completion-v1/audit_warnings.py --check
```

FILES.json seals the compact package. Generated bodies, compressed per-warning
inventories, and original large runtime logs are separately hash-bound and
retained locally. No cleanup was performed by this completion preparation.
