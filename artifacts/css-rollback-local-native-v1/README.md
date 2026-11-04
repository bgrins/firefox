# Rollback candidate comparison

This local experiment compares the two-source A+B+D candidate against the completed current-stack baseline. The exact primary roster is A16+B16+D48. Live WPT probes are preserved, including the older D64 page. The C implementation remains excluded and stylist.rs is pinned unchanged.

The baseline completed 74 PASS / 6 FAIL with three OK page harnesses. It used the already built current branch plus the separate three-file empty ArcSlice repair. That library patch remains identical in both roles. revert-rule is enabled explicitly; this is not release-default evidence.

run.py derives from the completed reversible font diagnostic owner. It gates on pinned completed baseline observations, checks the source/index/application association, backs up the application, writes only the two captured Rust candidate sources in place, builds binaries, runs the primary and control suites, and restores original sources/application. Both process registries must be empty before restoration. It records execution and restoration separately from semantic acceptance.

CONFIG.json remains disabled until the control baseline and supplemental raw audit are complete and their evidence is bound. The invocation requires its exact SHA256. compare.py requires the same 80 callback names, six FAIL-to-PASS changes, and preservation of every original pass. A successful comparison still does not prove full Rust refinement, release exposure, or standalone landability. The retained controls and independent restoration audit remain separate gates.

No signing bypass, push, Try run, or external submission is part of this experiment.
