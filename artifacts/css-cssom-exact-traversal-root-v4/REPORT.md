# Root review of traversal v4

The complete candidate GetTransformMatrix body and the v3-to-v4 delta were read.
The delta only routes null metadata requests to the existing CommonLayout loop
when flags are empty and both viewport types are Layout. In that state the
position selector reduces to GetPosition and the stopping predicate reduces to
IsTransformed. The source-transformed/zoom branch precedes dispatch unchanged;
ancestor equality still precedes the stop predicate. TrackWide=false keeps the
legacy grouped arithmetic and does not write metadata. Provider stability and
legacy defined arithmetic remain premises; this is not universal native safety.

All four retained original source files match the current worktree. The three
candidate files other than nsIFrame.cpp are byte-identical to v3. The full replay
controller was read, including comparison of mutant ROWs to original output.
That independent reference detects the force-common mutant even when both null
and requested paths agree incorrectly. Targeted null flags and visual mutants
must fail their specific assertions. The outer verifier passes with the pinned
manifest. Root has not duplicated the producer/reviewer compiler runs.

Independent source and driver verifiers pass, and both complete reports were
read. Their scoped GO supports a reversible browser experiment after fresh
input/index binding. Root also authenticated both 154-file producer replay
rosters and reconstructed the original-row and targeted null-mutant checks.
No v4 performance result or native acceptance is claimed by this checkpoint.
