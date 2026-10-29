# Compact raw-index observation refresh

Enabled after root review 878b7f, for root-owned execution after the configured Gecko check failed with
Cargo exit 101 and ten serde trait errors. The six source files were restored;
the saved full preservation check passed. This refresh neither reclassifies the
compile failure nor accepts the candidate.

The authenticated compact PRE/POST records differ only in the root raw-index
hash and its derived snapshot digest. Their semantic index, nested raw index,
flags and old canonical epoch hash match. The runner verifies the full current
state in memory, joins it to the saved POST digest, checks all six restored
source identities/modes/hashes and absent compiler groups, then changes only
canonical `raw_index_observation.current`. ROLE, OWNED and every other epoch
field remain unchanged. The cause of raw drift is not established.

No full epoch copies are saved. Compact receipts record old/new raw hashes,
resulting epoch digest and preservation status. An owned write failure restores
the old canonical bytes; uncertain recovery retains the lock. Once a successful
refresh receipt is published, a later lock-release failure cannot roll back the
epoch and leave a stale success receipt.

The actual terminal was reported by root as session 13662, launch e9cfe6,
terminal d41692/1. Exact underlying compile/restoration evidence is pinned;
the preparing agent did not run the compiler or this refresh.

Root-only command:
`/Users/bgrins/venvs/firefox/bin/python -I -S -B artifacts/css-contextual-easing-typecheck-raw-index-refresh-v1/run.py --run FILES_SHA256`.
`--check` authenticates saved projection/evidence without live verification or
canonical publication.
