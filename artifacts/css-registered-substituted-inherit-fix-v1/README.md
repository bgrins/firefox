# Substituted inheritance restyle dependency

A noninherited registered property can receive inherit after substitution.
The helper copied the parent value but did not record INHERITS_RESET_STYLE.
When only parent reset values changed, conditional recascade could skip the
child, leaving an obsolete inherited value. The candidate marks the dependency
before both the Some and None parent cases. Root defaulting and inherited
registration routes keep their existing behavior.

## Local validation

The paired shared-tree macOS builds exit 0. Seven new subtests change from three
FAIL and four PASS to seven PASS; all 37 adjacent subtests remain PASS. Both runs
have five OK harnesses and complete suites. Cases include numeric parent changes,
an additional ordinary reset-property mutation, direct inheritance and unset
controls, and universal invalid→valid→invalid parent changes with a var consumer.
Sources, tests and selected binaries remain stable within each phase.

The build monitor prints four existing KeyError export diagnostics per build;
actual compilation/link and Mach completion succeed. Scoped formatting exits 0
and changes no bytes. Lint exits 0 with one warning: the WPT is excluded by the existing ESLint ignore pattern. The
initial request to format the entire dirty tree was rejected by automatic
approval review, so the executed formatter was restricted to this native file
and WPT. Exact two-file patch apply/reverse passes on the branch and retained
upstream base. No isolated upstream or release-browser runtime is claimed.

Discovery was source audit followed by browser reproduction. Independent source
review traces the reset-only difference, conditional hint and stored-flag check.
The compact formal companion and independent final evidence review are separate
records; whole DOM scheduling, map/registration and native compiler behavior are
not established by these finite tests.
