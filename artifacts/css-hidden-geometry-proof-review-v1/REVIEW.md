# Independent hidden-geometry proof review

Verdict: **ACCEPT_SCOPED_MODEL_AND_EXTRACTED_CALIBRATION**. This is not acceptance of either native repair.

## Mathematical claim

The 30 results concern a single frame with a Boolean projection of subtree dirtiness, geometry, and an optional measurement. The key includes current computed size, containing-block size, border/padding, minimum, maximum and available block size. A clean matching-key hit preserves the entire frame. A miss publishes either zero (hidden early return) or the supplied layout provider's output and caches its block-size projection. The last added result instantiates the reported sentinel-to-zero containing-block key transition without deriving native caller reachability.

The provisional repair marks a hidden miss dirty. `geometryQuery` then synchronously invokes a nonhidden measurement of the same frame if the queried frame is dirty and has a hidden ancestor. Under that *definition* it recovers the supplied provider output. The theorem does not derive the actual document-flush traversal, identity, termination, or provider correctness. In particular, an arbitrary zero-returning provider still produces zero after recovery.

The general results preserve old behavior on hits, nonhidden calls and already-dirty frames. Hidden dirty misses remain dirty until forced layout; cache equality alone cannot establish geometry freshness. The repeated-query theorem is a no-work result even with a different next key, not a freshness guarantee. The explicit clean-descendant countermodel retains the caller limitation.

The fixed-block specialization is a separate arithmetic provider, not a proof of nsBlockFrame sizing. Mathematical Int operations do not establish nscoord representability. The lower/upper hypotheses in `fixed_block_dimensions` are necessary to simplify its clamp.

## Inspected native correspondence

Read all model statements/proofs, audit and false-claim files, both row generators, extractor, replay controller, all facade declarations and generated-body source sites. The exact source key, measurement hit/miss, FinishReflowChild, DidReflow, hidden predicates and four PresShell methods agree with their stated projections. The logical Finish method publishes SetSize even under NoMoveFrame. Hidden DidReflow removes only IN_REFLOW. The actual clean-frame early return precedes hidden ancestor collection. The three retained constructors establish the zero-initialization chain, but the executable substitutes its own LogicalSize/ReflowOutput constructor, accurately disclosed.

The complete ordinary block body is retained, but only its hidden-parent/no-next-continuation guard is extracted; the rest is replaced with Provider. ReflowChild, frame-property ownership/update, overflow effects, SVG notification, percentage observer effects, physical conversions, statuses and document flushing are simplified or excluded. `FrameNeedsReflow` only increments a request counter in the facade; the harness supplies a synchronous measurement callback. GetContent is modeled by frame identity. No general content/frame alias, anonymous-frame, continuation, orthogonal-writing-mode, callback mutation or lifecycle theorem follows.

The source role is historical HEAD 99a9ca84 plus the provisional miss-only AddStateBits patch. This review does not bind the newer MarkPrincipalChildrenDirty candidate, nor declare the provisional patch sufficient to land. The native matrix uses containing-block changes for its unequal-key cases. Independent kernel challenges additionally use only the original computed-size key field; they do not establish native browser call-path reachability.

## Replay and integrity

Authenticated external FILES `a4dc6e88cf8bd4f431875a619017339a2d4ac658d0588ba3585def2d9e419c8c`, FREEZE `10841cf8256c14b71d71adca663aa56c5aed0bd846def2ede2cdf1913c3e3cc9`, and replay controller `c8e39cd567aac92317f1b5156578f73f647cdfb039e479e1904965567321c486` before execution. Fresh manifest-only relocation passed 30 audits, 15 bindings, four 192-row original/repaired O0/O2 comparisons under UBSan, six compiled mutants at both optimizations, and four intended false-claim failures. Exact theorem-to-audit name equality was checked independently; the producer runner itself checks count/axiom allowlist rather than exact names.

All compiled mutants terminate successfully without sanitizer stderr. Differing rows at each optimization are: dropped dirty mark 32; reuse dirty cache 64; omitted containing-block key 32; skipped size publication 80; forced clean query 96; ignored forcing set 80. These are changes in the extracted source control/key predicates or publication operation. The first differences demonstrate respectively lost recovery, inappropriate reuse, a changed reuse decision, stale premeasurement geometry, an extra forced request, and repeated zero publication. No syntax/compile/crash rejection is counted as mutant detection. Four Lean false claims fail specifically because decide proves their propositions false.

Nine independent kernel results pass: original computed-size-only miss; old zero retention; provisional direct recovery; wrong provider output despite recovery; absence of a hidden ancestor; clean descendant stale width; same-key corrupt geometry; changed provider after clean recovery; and arbitrary supplied forced key/provider. The first compile exposed only an ambiguous unqualified `measure` in the reviewer's simp list; its failed source/log are retained. Qualifying `Hidden.measure` yields all nine results with no warnings or sorryAx, using at most propext.

Ten independent controls pass: intact verification and nine negative mode/shadow/extra-file/empty-directory/symlink/tamper checks, all without output creation. The controller's pre-import isolated/no-site/nonoptimized guard and disabled bytecode prevent local import side effects in the advertised entrypoint. Resolved output paths must be new and disjoint from the source tree. The producer does not explicitly reject every nonregular file type before hashing; FIFO/socket fail-closed coverage is not claimed. This review checked actual entries as regular files/directories before copying and rechecks nested closure when verifying the review.

Tool executable hashes/versions are checked; SDK/dynamic libraries/full Lean installation are not packaged. This is a local trusted-toolchain replay, not hermetic compilation. The producer controller removes its generated executables/olean after retaining sources/logs; the review additionally removed its own completed Hidden.olean with a size/hash receipt. No browser, Gecko build, native edit or Git mutation was performed.

Replay from any review copy (choose a new absolute output outside the copied capsule):

```sh
python3 -I -S capsule/replay.py --manifest-sha a4dc6e88cf8bd4f431875a619017339a2d4ac658d0588ba3585def2d9e419c8c --out /ABSENT/EXTERNAL/OUTPUT
```

To replay the independent challenges, compile capsule/lean/Hidden.lean into a separate output directory using the pinned Lean executable, then run Independent.lean with LEAN_PATH set to that directory. Exact executed commands are retained in independent/; development-failure/ records the superseded failed attempt.

## Acceptance limit

No mathematical or inspected-source projection blocker remains within this component's stated scope. Neither this result nor finite native agreement closes descendant dirtying, complete layout scheduling, cache lifetime, numerical ranges, full CSSOM observations, or the full allocation F1–F16/F11/F12 project. Later browser evidence concerning the partial patch is not independently revalidated by this formal review and is not needed for its conditional conclusion.
