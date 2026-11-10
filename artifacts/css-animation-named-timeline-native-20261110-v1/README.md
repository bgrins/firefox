# Named-timeline admission during the animation drain

Initial styling of a revealed scroll-timeline provider rebinds an existing
ancestor animation and requests work on that ancestor. Both reveal callbacks
return the 10px base font after starting at 20px; the unchanged-lookup scope
control stays at 20px. This reaches a non-descendant producer, not an infinite
cycle or a new browser defect. Repair #160 remains held.

Ten native files carry temporary tracing on the previously checked producer-local
handoff plus dependency-drain candidate. Scroll-driven animations are explicitly
enabled and direct CSS display animations disabled. The new hooks record lookup
equality/deferral/rebinding, returned timeline identity and actual timing
eligibility. The eligibility hook sits inside the existing successful guard and
does not evaluate the predicate again. Timeline object kind is separate from
whether its current time is resolved. Animation pointers use the common base.

All three callbacks pass with one OK harness completion. The original animation
identity survives. After provider reveal its timeline source is provider and its
progress is unresolved/pending; scope-only admission retains fallback and 50%
progress. These post-getter API observations alone do not establish native
same-call delivery. The analyzer separately joins exact task, rebind, request,
hint and installation records.

Root independently verified restoration of the full application, ten sources,
three build extras, baseline binary hashes, checkpoint/index and absent process
groups. The temporary WPT and about 1 GB backup were removed. The active objdir
and manual browser remain available. The known Mach export progress-monitor
KeyError was nonfatal; the build command exited zero.

`prepare.py` reconstructs thirty stage/source hashes from b6f9b206df9c using the
retained patches without offsets or fuzz; root replayed it independently.
`--materialize` recreates source copies only when all three stage directories
are absent. `run.py` requires isolated, non-optimized Python, a fresh output
name and this machine's configured objdir/pinned baseline. This is a local
experiment, not a portable build environment. The restoration receipt binds
checkpoint 4cda7885b649; its HEAD/index audit intentionally rejects later commits.

The provider later recascades with an existing primary style and does not
regenerate its timeline task in this run. A single backward tree edge does not
show renewal. General causal closure, native-to-Lean refinement and termination
remain separate obligations. The follow-up source investigation checks animated
names/scopes and normal-management gates before another browser discriminator.

Root independently replayed the analyzer and all 33 expected-reason negative
controls, and authenticated both task-mask source excerpts. The two positive
cases each deliver one full-key request cohort; the scope control delivers none.
No malformed tagged records or caps occur. Verified reconstructible source
copies were removed after exact patch replay. See ROOT-REVIEW.json and
ANALYZER-REVIEW.md for the bounded result and its limitations.
