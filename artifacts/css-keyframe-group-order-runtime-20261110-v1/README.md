# Percentage group-order browser comparison

This reversible experiment compares the retained #171 browser with the copied
bug-1778402 candidate. Both variants install the same strengthened WPT page.
Only the candidate installs the two native source files and rebuilds. Existing
failure metadata remains unchanged during the experiment; delivery removes the
single repaired expectation separately.

The nine-page inventory has exactly 86 callbacks and nine harness endings.
The baseline must match its complete frozen status vector: 75 PASS, 11 FAIL,
and nine OK. The candidate must improve exactly the existing group-order case
and the new interleaved-offset/logical-declaration case. Every other result and
diagnostic message must match; messages on the two intended improvements are
excluded. Attribute mutation and named-range controls must remain passing.
Twenty-five synthetic rejection controls exercise malformed event streams,
inventory loss, key collisions, missing improvements and unexpected diagnostics.

Run with the pinned HEAD and clean tracked tree:

```sh
python3 -I run.py baseline baseline1
python3 -I run.py candidate candidate1 baseline1
```

The runner authenticates all frozen inputs and retained binary samples, backs up
the complete application and three explicit build/test files, and checks owned
process termination before restoration. Every touched source, including the WPT,
is restored under a concurrent-edit guard. Full content/type/mode restoration,
unchanged HEAD/index and test/config pins are required before backup removal.
Build intermediate objects are not rolled back. The runner and analyzer derive
from the signed snapshot experiment; `WRAPPER-ORIGINS.json` records that origin.

The preparation checks are not browser results. Actual outcomes belong in each
run's `RESULT.json`, raw logs and independent terminal review. No native repair is
accepted merely because a command exits successfully. This bounded optimized
comparison does not close the separate missing-pseudo CSSOM debug gate or prove
general C++ memory safety/performance equivalence.

The completed comparison passed: 75 PASS / 11 FAIL became 77 PASS / 9 FAIL,
with nine OK harness endings in each run and exactly the two intended improvements.
All other statuses and messages match. Build and WPT lint succeeded; independent
review verified full restoration and backup/process cleanup. See
`ROOT-ACCEPTANCE.json` and the sibling runtime-review capsule. Four nonfatal Mach
tier-monitor tracebacks are retained in the successful build log. Native delivery
and the final committed-source build remain separate from this comparison.
