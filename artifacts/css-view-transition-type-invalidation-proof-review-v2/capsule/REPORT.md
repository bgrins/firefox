# View-transition type invalidation: bounded formal companion

## Result and scope

The model proves that effective mutation of the active transition preserves a cache-coherence obligation when it schedules subtree rematching, and that a complete delivered flush restores observations after arbitrary finite mutation/flush histories. An explicit Boolean selector and ordered-rule evaluator defines the expected values. Freshness is derived from executing that evaluator for covered subjects; it is not a premise asserting correct final caches.

39 named theorem audits cover general statements and concrete counterexamples. Four local Lean modules compile. The model includes successful, no-op, failed and old-transition operations, partial/full visits, root/descendant/pseudo subjects, coalesced pending work, and latest-membership rematching. It preserves the counterexample where synthesized old active-state flags retain current types and lose a Delete dependency.

The eleven source bindings include complete formatted Add/Delete/Clear/TypesChanged/nsLayoutUtils bodies, original methods, the retained RestyleManager dispatch/state snapshot bodies and generated setlike helpers. Five changed/current bodies execute with explicit provider substitutes in the C++ calibration. All 15,234 fixed cases and 51,702 snapshots agree across source-shaped C++, Lean, and a separate bitset oracle. The historical source reproduces six stale-style differences among the eighteen WPT operation projections. Four compiled C++ mutants and three Lean semantic mutants are required to be distinguished by the replay.

Read SOURCE-CONTRACT.md for exact boundaries. The pending Bool is conservative work debt, not Gecko's dirty-bit layout. Traversal liveness is not proved. A connected/nondestroying restyle manager and no in-traversal reentrancy are required in addition to Environment.live's root/composed/prescontext flags. Real resolver translation, subtree/pseudo traversal, CSSOM flush delivery, generated JS Set/atom providers and lifecycle cutpoints remain explicit obligations. Error histories need continuing representation consistency or a new consistent cutpoint. Initial duplicate elimination and all-CSS/browser correctness are separate claims.

## Browser relationship

Root's retained final source and paired-WPT receipts report 6 FAIL/36 PASS before, 42 PASS after, with stable source pins. The revised eighteen tests observe root/descendant styles, their ::before pseudos and (at ready) the transition-group pseudo. Existing tests supply the remaining rows. This companion does not rerun Firefox or promote finite browser success into a proof of the admitted backend.

## Replay

Authenticate FILES.json and FREEZE.json against externally supplied hashes before dispatch. Then:

```
python3 -I -S /absolute/path/to/check.py --output /fresh/external/output
```

The top checker validates the closed regular-file/inferred-directory roster, every input hash, retained source/evidence identities, pinned compiler executables, full body extraction, kernel axiom roster, three-way calibration, and semantic mutants, then reauthenticates. It rejects optimized/nonisolated/site-enabled execution before imports beyond builtin sys. Installed Lean standard libraries, C++ headers/compiler resources, runtime libraries and OS are trusted; executable pins are not full toolchain closure.

Producer fresh/relocated replay and unsafe-mode/roster receipts are stored separately so this source capsule stays immutable. Independent review and root acceptance remain separate gates. All native/browser/WPT/Git writes belong to root; this work only writes owned proof/calibration artifacts.
