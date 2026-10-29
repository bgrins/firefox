# Successful-check raw-index observation refresh

Enabled successor of the executed v1 refresh after root review f5f559. The only code changes require
the actual successful retry: session 25662, launch 349cfa, terminal a9684b/0,
Cargo exit 0 in 32.05 seconds, successful source restoration and full state
preservation. The earlier exit-101 compile failure remains unchanged evidence.

All publication, ownership, rollback, full in-memory verification, source/flags
checks and process-group checks are unchanged. The refresh changes only
`raw_index_observation.current` from `307079be...` to `9c8cfe22...`; it does not
save another epoch copy, change any source or binary, or accept the integration.
ROLE and OWNED remain identical. Raw drift has no established cause.

Root-only command:
`/Users/bgrins/venvs/firefox/bin/python -I -S -B artifacts/css-contextual-easing-typecheck-raw-index-refresh-v2/run.py --run FILES_SHA256`.
