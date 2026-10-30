# CSS verification continuation

149 accepted native fixes remain committed across 150 tracked IDs. Held repair
120 remains excluded. The two newer math proposals are validated together and with the committed provider but
are not installed or counted as accepted. HEAD remains ecfe313d582a.

| Work | Actual evidence | Next obligation |
| --- | --- | --- |
| Min/max contextual infinity | Individual 472-case comparison repairs 14 targets; combined run retains all authored coverage | Publish research and one source/two-WPT commit |
| Logarithm special values | Individual 102-case comparison repairs 15 targets; combined run retains all authored coverage | Publish research and one source/one-WPT/metadata-deletion commit |
| Combined math interaction | Fresh 578-case run repairs all 33 targets, including four cross-operator probes; 576 PASS and two preserved legacy FAIL; 60 authored checks PASS; 561 unchanged control/ending signatures, 16 endings | Provider-free comparison passed; publication pending |
| Contextual easing | Earlier 315-case comparison and isolated Servo checks remain scoped evidence; three animated-input callbacks prepared and statically checked | Fresh original/candidate measurements after math publication work; keep the metadata-refresh oracle tentative |

The combined owner finished as session 83012, terminal 0fce51, exit 0. Root
independently replayed both complete raw streams in 30831/1a92bc/0. The native
build succeeded; the browser harness returned 1 because five repaired existing
cases still carry comparison-only expected-FAIL metadata. The strict comparison
passed. The build log contains the previously seen export-tier progress
exception, so this is not a claim of a diagnostic-free build.

[Comparison receipt](../css-minmax-log-baseline-runtime-1/CANDIDATE-ROOT-REPLAY.json)
records the exact scope. Original source and application were restored; the
verified 1,008,605,176-byte backup was removed. A raw Git index byte change was
reconciled after full semantic/state checks, changing only its recorded hash.
Actual refresh: 43378/0c512d/0; independent one-field reconstruction: 4e47e8/0.
That intermediate epoch was dd990a8ecd6176d247e6d5d3a58e58186d03ad6b948639eef0e2690fa693845d.
The cause of the raw byte change is unknown.

## Next actions

1. The provider-free comparison is complete: session90981/22d34a/0;
   root independent replay90781/882d4c/0. The committed provider built
   successfully, and all 578 row plus 16 ending signatures match the successful
   combined-with-provider run. The 33-target/561-signature gates also pass.
   Both owned sources, the held provider and original application were restored;
   another verified 1,008,605,176-byte backup was removed. This establishes
   bounded passing behavior without that provider, not a provider-free original
   causal delta or clean-upstream behavior. See the
   [provider comparison](../css-minmax-log-provider-free-runtime-1/CANDIDATE-ROOT-REPLAY.json).
   Refresh99485/45701e/0 and independent reconstruction88b839/0 updated only the
   new raw-index observation. Current epoch is
   e73e66132730fca8b1cf5bde149016653c3e4a1f1a5f0ed29ab2551d291c4064.
2. Publish completed research before the two native commits. The
   [reviewed payloads](../css-minmax-log-native-payload-review-v1/README.md)
   contain exactly three paths each. Remove the five obsolete log expected-FAIL
   annotations in the log commit; keep unrelated legacy failures unchanged.
   Accepted relative-length transport fix 119 remains a tested prerequisite for
   contextual evidence. Other same-file predecessors are recorded as source
   lineage, without inventing semantic dependencies.
3. Add actual signed native commit IDs to the ledger only after acceptance.
   The V66 research signing attempt failed in 1Password with “failed to fill
   whole buffer”; session 14309/92a94d/1, Git exit 128. Failure verification
   confirmed unchanged HEAD, empty staging, retained selected bodies and no
   transition lock. Its prepared inventory now needs a fresh checkpoint, not
   replay under an obsolete state binding. No unsigned fallback or automatic
   signer retry is planned.
4. The six-case literal/generated-zero observation is complete: actual
   61927/d7d097/0, root exact replay62901/96e96c/0. Both literal-negative
   cases fail only at the final value assertion (0.25 observed versus 0.75
   under the current written rule); all four positive/generated controls pass.
   Source/application/canonical state and cleanup are verified. This is evidence
   for known CSSWG issue7472, not automatically a new implementation bug.
   Obtain exact-case release/interoperability evidence and the full issue
   disposition before any literal-only normalizer. Do not normalize all
   computed zeros: that would destroy valid arithmetic-generated negative zero.
5. Continue easing ownership/movement and animated-input investigation. The
   [oracle review](../css-contextual-easing-animated-input-oracle-review-v1/README.md)
   supports the expected arithmetic and dependent-style behavior but does not
   establish an explicit unchanged-keyframe metadata refresh algorithm. A
   failure of the new tentative probe is proposal-boundary evidence, not yet
   an unqualified release-bug claim. Its original-only runner remains disabled.

## Formal scope and preservation

The new [literal-zero policy model](../css-literal-negative-zero-model-v1/README.md)
passed 16 theorem audits and rejected four false claims (57396/34f41d/0).
Root authenticated all 22 model payloads, read the model/audit/rejection logs,
and joined the exact fixture assertions to its six-case quarter-unit vectors.
The browser agrees with the sign-preserving policy for these six samples.
Independent review found no blocker. The observer distinguishes positive zero,
negative zero and NaN, not every finite semantic class; dimension erasure is an
explicit model choice. Source/spec research preceded the model. Neither the
model nor these observations settle CSSWG7472 or prove parser/native refinement.

The existing min/max winner model and logarithm dispatch model retain their
bounded assumptions; this browser result does not prove native refinement or
all IEEE operations. Canonical Lean coverage remains unchanged (11,840 recorded
audits, 12,438 cases, 173 false cases, 2,155 fingerprints). Bloom milestones 1–6
remain complete within their documented scope. The broader objective remains
observable CSS bug finding and extension of the standalone spec model.

The V66 audit found all 563 untracked paths expected, including 68 prototype
files matching committed recovery copies. The held provider is still the sole
tracked native edit. The twelve obsolete Lean build caches removed earlier
remain removed; source archives and evidence were retained. All work is local.
