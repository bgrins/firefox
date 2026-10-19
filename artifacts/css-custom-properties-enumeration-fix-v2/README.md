# Final custom-property enumeration comparison

19 October 2026. Final formatted candidate sources and revised WPTs; native and
formal acceptance are separate. This supersedes the diagnostic comparison's
incomplete original-source pinning, without changing its retained evidence.

## Results

| Variant | PASS | FAIL | Harnesses OK |
| --- | ---: | ---: | ---: |
| Original | 30 | 11 | 7 |
| Count and indexed filtering | 38 | 3 | 7 |
| Count plus iterator repair | 41 | 0 | 7 |

`check-results.py` validates the exact 41 identities, seven complete harnesses,
source/test/runner stability, build-to-runtime binary hashes and terminal suite
events. Every native file is named explicitly even when it matches HEAD. The
build driver additionally checks neighboring modified sources and new WPTs
before and after each build/test transaction. All three builds returned zero.
Each retained four preexisting build-monitor `KeyError: 'export'` diagnostics.

The ten-case invalid-value WPT adds last-value removal/restoration and transitions
across inherited/non-inherited maps to the original eight cases. It distinguishes
invalid from valid-empty through enumeration; only known valid-empty controls
normalize serialization whitespace. This avoids embedding an unrelated empty
serialization requirement in the enumeration test. Exact invalid serialization
and ordinary value assertions remain.

Seven shadowing cases and two restoration-chain cases exercise iterator behavior.
The count-only repair leaves three duplicate-iteration failures; it introduces no
new failing row in this matrix. The final candidate repairs all eleven original
failures. This is finite shared-tree macOS evidence, not isolated-upstream or
release-browser testing, nor a proof of all CSSOM behavior.

## Reviewable patch shapes

- `count-native-wpt.patch`: the map count/filter change and ten-case WPT.
- `iterator-native-wpt.patch`: the iterator loop target and seven-case/two-case
  WPTs, applied after the count repair in the working stack.
- `iterator-standalone-native-wpt.patch`: the iterator repair with necessary
  count support and all three WPT files, applicable without the preceding fix.

`check-packaging.py` applies and reverses all three forms against the branch HEAD
and original upstream base using temporary indexes. It checks exact changed-file
rosters and every resulting native/test blob. All six checks pass; the primary
index remains untouched. This proves applicability, not upstream runtime behavior.
The standalone alternative still needs a signed local commit and ledger entry.

## Formatting and lint

Scoped formatting changed only line wrapping in the indexed-access chain. Full
scoped lint returned zero with no errors. Its three warnings are the three WPT
HTML files matching ESLint's ignore patterns; a warnings-enabled ESLint run
returns one for those warnings. The whitespace-only check and all three extracted
JavaScript syntax checks pass. Logs and `FORMAT-LINT.json` retain the distinction.

## Formal scope and remaining gates

The iterator and count producers target these exact formatted snapshots. The
iterator's live-count premise and the count component's raw-enumeration premise
must be connected in the separate composition proof. Native container, Arc,
compiler, machine bounds, payload projection and registration-routing assumptions
remain explicit. Per-map uniqueness does not alone establish disjoint inherited
and non-inherited maps across all registration histories.

Independent source/test/runtime review found no blocker. Complete formal
authentication/replay, joint composition, scoped root acceptance and signed
native/standalone commits remain. The ledger still counts 73 committed repairs.
