# Initial animation-only admission: native diagnostic

The producer-local combined candidate reaches previously unstyled descendants
inside an animation-only traversal after one paused SMIL display reveal. The
first getter returns 512px; ordinary reveal and literal-font controls also pass.
This establishes a reachable initial-style exception, not recurring destruction
or recreation, global convergence, or a new defect. Repair #160 remains held.

## Experiment

The semantic candidate is the previously checked producer-local handoff plus
dependency drain. Eight native files carry temporary tracing. CSS display
animation is explicitly disabled; the reveal uses SVG SMIL. Three callbacks run
in separate iframe documents and record stimulus/getter boundaries, four target
identities, paused animation state and the repeated endpoint read.

The trace records initial admission, restyle kind, absent old primary style,
actual task masks, task queue/execution/return and installed styles. Document
calls and drain iterations are explicit. StyleNewSubtree has a separate call
identity and distinguishes default and final animation traversals; its exit
marker runs after traversal-guard teardown. Rust emits each record as a complete
line. The hooks do not establish universal native-to-model refinement or remove
every possible output transport failure.

Runtime1 built successfully and returned three PASS subtests with one OK
harness completion. The full application, eight native sources, three extra
build files, baseline binary hashes, HEAD and index were independently checked
after restoration. Both owned process groups were absent; the temporary WPT
and approximately 1 GB backup were removed. The active objdir is retained.
Mach emitted its previously observed progress-monitor KeyError for export; the
build command nevertheless exited zero and completed successfully.

## Replay and scope

`prepare.py` reconstructs base, semantic and instrumented sources from pinned
Git revision ed3873319761 and two exact patches. Root replay checked all 24
source hashes with zero patch fuzz or offsets. `--materialize` recreates the
three source directories only when none exists. `run.py` requires isolated,
non-optimized Python and a fresh output name; it records command ownership and
restores the saved browser after success or failure. It uses this machine's
configured objdir and pinned baseline, not a portable full build setup.

The independent restoration receipt authenticates historical checkpoint
bc8b09c8d722. Re-running that audit after later commits intentionally rejects
changed HEAD/index. Raw logs and failed analyzer attempts are retained as
evidence, not silently treated as successful checks.

Root independently replayed the final analyzer and all 22 expected-reason
negative controls. The 43 requests in the two animated modes are conserved into
20 delivered cohorts, with drain groups 4, 3, 2, 1 in each mode. Four initial
AnimationOnly tasks occur in the SMIL case at iteration zero. No malformed
tagged records occur; the one cap belongs to another process after all measured
intervals. See ANALYZER-REVIEW.md and ROOT-REVIEW.json. Initial work after one external SMIL seek is finite starting work;
SMIL is sampled before iteration zero rather than in the repeated compositor
loop. Correct final values alone are insufficient for initial-admission or
delivery claims. Later same-rank lifetime renewal remains a source/refinement
obligation.
