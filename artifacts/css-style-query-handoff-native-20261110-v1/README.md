# Query-only native handoff comparison

The two-file candidate for bug 2085413 changes the exact 26-callback selection
from 17 PASS / 9 FAIL to 26 PASS. All five harnesses finish OK in both runs.
All twelve existing held-font regression callbacks pass on both sides; their
source files are unchanged. These nine failures are manifestations of the one
known animated style-query invalidation issue, not nine separate bugs.

The native build exits zero after 53 seconds. The known nonfatal Mach progress
monitor `KeyError: export` remains in the raw build log; the final build receipt,
new binary hashes and exact source/fixture hashes authenticate the executed
candidate. No new compiler warning is reported by the final build summary.

The candidate preserves the two query masks per producer, then restores a normal
dirty path after workers join. Its private rooted-path set avoids repeated full
ancestor walks. The existing font handoff and document drain loop are unchanged.
Patch SHA-256 is 75ab9dc8feec80bae0ac17a4b3cdf141373372283c2cb6721491dd7ea3993d1b.
Source and independent reviews are retained in the separate handoff-review and
handoff-independent capsules. The final import ordering differs from an earlier
review copy only in the order of two use declarations.

## What was exercised

The reduced named/unnamed color tests, ordinary controls, literal timeline-name
and timeline-scope queries, depth-256 named consumer, eight target siblings,
descendant pseudo, hidden subtree, nearest named boundary and registered
noninherited custom-property case all pass with the candidate. The ordinary and
hidden-query controls already passed before it. On/off/on query toggles are
checked in the timeline and boundary-control fixtures.

STYLO_THREADS=1 is explicit for this comparison. The sibling control has one
animated producer with eight target siblings; it is not evidence for multiple
parallel producer admissions. Hidden color access is tested, not hidden-then-
reveal. A compact final delivery fixture and multi-producer/nearest-override/
reveal controls remain the planned final acceptance step before the repair commit.
No claim of release exposure, general timeline convergence or native memory
safety is made. The held font/drain repair remains held.

## Reproduction and cleanup

run.py accepts a new output directory and optional `candidate` argument. Without
that argument it uses the existing scope-cache baseline application; with it,
it installs the two authenticated source candidates and builds binaries. It
runs three temporary WPT pages and the two unchanged existing font pages.
SOURCE-ROLES.json, FIXTURES.json, EXISTING.json and ROSTER.json specify the exact
inputs. All test output is redirected to retained log files.

The transaction restores both native files, the full baseline application and
three build extras. Root independently verified both restorations, unchanged
Git checkpoint/index, absent owned process groups, removed temporary WPTs and
removed approximately 1 GB backups. The active objdir remains. Historical
receipts bind cf80bc460ce4; their HEAD/index assertions are expected to reject a
later checkpoint. ROOT-VALIDATION.json authenticates raw events independently
of the runner's summaries. No production source or WPT is left modified by this
comparison.
