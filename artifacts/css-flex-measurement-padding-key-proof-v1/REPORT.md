# Bounded measurement-key companion

Status: implementation and replay gates are recorded in the separate receipt package. This is not root acceptance or a proof of full cache freshness.

Fourteen Lean results establish original-key/input equivalence, exact candidate/input equivalence, all four padding components, preservation under unchanged padding and original rejection, caller present/dirty guards, independent shared-baseline equations and discriminating counterexamples. Four individual-component omission predicates have compiled witnesses and corresponding rejected false claims. All values are arbitrary mathematical integers in the general results; native representation assumptions are explicit.

Complete old/new cache classes compile with admitted getter/primitive facades in debug, release and UBSan modes on 640 independently constructed cases. Two actual-class semantic mutants are required to disagree with the independent fieldwise oracle. This is finite native agreement, separate from the universal model proof.

The repair is a strict strengthening of key equality. It leaves the old decision unchanged when border/padding agrees. Equal candidate keys do not prove external provider stability, as an explicit theorem demonstrates. The retained baseline witness explains why a correct final frame/cache update cannot retroactively repair an earlier alignment choice. See `SOURCE-ADMISSION.md` for exact mappings and excluded claims.

Replay from a source-only copy: `python3 -I -S check.py --output ABSENT_ABSOLUTE_EXTERNAL_DIRECTORY`. The top checker authenticates a closed regular-file/directory roster, all hashes and source bindings before compilation, then rechecks after replay. It requires isolation, disabled site loading and no optimization before importing other modules. Lean and clang executable pins are checked; their libraries, OS and runtime remain trusted. External authentication of FILES/FREEZE remains the consumer's responsibility.

This component precedes the separately reviewed native/WPT repair. No native source, WPT, Git state or Firefox build was changed by its producer.
