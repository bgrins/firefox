# Contextual keyframe dependency handoff: Gecko typecheck

The sealed six-source prototype passed Cargo check of the complete configured Firefox Rust graph, exit0, in18.80s. This checks the Gecko configuration and geckoservo callers. Servo-only cfg paths remain untypechecked; this is neither a Servo build nor a linked-browser or lifecycle result.

All source overlays were restored. Original native/binary/research and Git semantics were verified, with only the raw-index observation reconciled. ROLE/OWNED provenance is unchanged; owned compiler groups were absent. The existing objdir was reused. The existing partial-v5 misplaced documentation warning remains in the log and is unrelated to this handoff.

Contextual steps parsing remains guarded. Six browser fixtures are unexecuted. Complete invalidation, animated dependency policy and open CSSWG issue14246 remain activation requirements. No accepted-fix or canonical-library increment.
