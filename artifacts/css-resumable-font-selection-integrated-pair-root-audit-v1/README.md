# Independent restoration after incomplete paired browser run

Actual main owner1002/36b5f4 exited1 after the candidate minimum-off WPT crashed. Root audit78962/f6e010/818ac8 exited0. It independently verified all three source hashes and identities, application/extras/binaries, index semantics, flags, canonical controls, all recorded process groups and12 owned WPT temporary roots. The main root process group is absent. The original application is restored; the raw index observation changed without semantic changes.

The failed owner retained its verified1,008,605,176-byte backup. The audit authenticated that retained inventory; it did not delete it or modify canonical state. This is restoration evidence, not candidate acceptance. Peer review caught and root added WPT temporary-root absence and dangling lock checks before execution. These additions were reviewed against actual helper schemas.
