# Unfinished work checkpoint

This patch preserves the current project working changes, including native prototypes, unaccepted probes and proof-tool changes. It is a recovery snapshot, not an accepted repair or a landable production commit. The 131 accepted bug fixes are already separate commits.

Apply `unfinished.patch` to the commit in `BASE.json` to reconstruct these exact source bodies. `SOURCE-PINS.json` authenticates every resulting file. Unrelated untracked directories, build products and the nested CSS library are excluded. The library is separately signed in its own repository.

The compact-owner build failed its 32-byte layout assertion. The corrective compact borrow has source review but has not compiled: both isolated test attempts stopped during Cargo setup. Transition descriptor regression tests previously passed after correction; current-provider browser failures and memory-reporting obligations remain open. The steps repair remains a separate unapplied research proposal with browser validation pending.
