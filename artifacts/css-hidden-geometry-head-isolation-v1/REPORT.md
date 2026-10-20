# Hidden flex: committed-source isolation

The exact committed native source experiment completed successfully. Both builds
and the 32-case browser probe exited zero. All 160 stage records equal the earlier
combined working-tree run, including all 32 failing stages. Removing the 20 dirty
tracked native files in layout/dom/servo therefore does not remove this fixture's
failure. This does not isolate one accepted commit from the rest of the branch.

The driver restored every original source byte and rebuilt successfully. HEAD,
all staged entries/content, and the source snapshot equal the preexperiment
snapshot. The installed source/build includes committed rectangle fix 103 plus
the preserved earlier working-tree edits. No candidate repair was kept installed.

A separate release158 probe changes an original cache-key input through ordinary
flex shrink: 12 of240 stages differ from calibrated visible controls. Eight direct
item stages return0×0, and four nested descendant stages retain the old100px width
instead of50px. All three repeated reads agree. That separate evidence establishes
preexisting release behavior, not the exact internal cache/callback execution.
See ../css-hidden-geometry-release-key-review-v1/REPORT.md.

Discovery began with browser mutation probes during normalization work; source
reasoning nominated the skipped-measurement/cache/dirty-state sequence. The release
probe then established independent exposure. The subsequent Lean model formalizes
that scoped sequence and its limitations; it did not independently discover this
browser failure.

The four-variant instrumented follow-up remains a separate experiment. No native
repair, complete cache/lifetime theorem, security impact, or new signed-fix count
is claimed by this checkpoint.
