# String/comment root checkpoint

No new defect established. Root read the complete producer report, generator,
checker, source-bound string/comment loops and proposed provider obligations.
The authenticated capsule has 54 inputs and 27 complete extracted bodies. A
fresh relocated replay passes 646 cases in both debug and release. These are
finite comparisons, not universal proofs or execution of the public parser.

The existing local Firefox build passes all 19 string/comment browser controls
and both BadString declaration-recovery cases. The eight outcome records from
the two existing tests match the previous numeric candidate run. They include
four expected failures. Source, configuration, resources and binary hashes are
stable before and after; this is the shared experimental build, not an isolated
upstream checkout. No native source changed or rebuild was needed.

Two details constrain interpretation of the existing failures:

- `escaped-eof.html` reverses the usual actual/expected assertion arguments.
  Browser serialization contains a backslash before U+FFFD in the identifier,
  dimension and URL cases; the test expects the replacement character alone.
  Token payload decoding is not thereby shown incorrect.
- `serialize-escape-identifiers.html` fails while accessing `cssRules` through
  an undefined `document.styleSheets[0]`. This run never reaches its round-trip
  equality assertion. Import-loading timing is a hypothesis, not a conclusion.

The static source witness executes comment directive handling but does not
assert source-map/sourceURL fields. All twelve obligations in the producer's
`PROOF-TARGET.md` remain required; complete comment observers are the next formal
component. Native heap/library/macro representation, packed line-counter bounds,
public parser cache/reset behavior and consumer composition remain open.

## Replay

Run the producer checker with `--run --output` pointing to a fresh directory.
For this exact browser build, `probes.py install` installs the two immutable
artifact probes into the WPT tree; `run-browser.py` verifies pinned inputs and
runs headless WPT. `probes.py remove` removes only byte-identical probe copies.
The retained browser input pins intentionally reject a changed build or source.
Slow command output is retained in this directory. The probes stay in the
artifact capsule; this checkpoint adds no proposed native/WPT repair.
