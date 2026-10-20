# Whole CSS in Lean: next implementation decisions

Three agents assessed coverage, architecture and maintenance against the existing
library and new source/fragmentation work. Root read the reports and the small
migration example, then replayed its ten checks. This is research, not a new
whole-CSS conformance claim.

## Conclusions

A complete model remains a plausible research objective. We have not established
that the current architecture scales to it, and cannot give a defensible
completion percentage or date. The main missing work is faithful interpretation
and composition: constructing the inputs our local proofs assume, preserving
observations across components, and tracking every applicable requirement.

| Workstream | Finding | Next concrete result |
| --- | --- | --- |
| [Coverage](coverage/REPORT.md) | The library's 127 overlapping historical records are not a whole-spec denominator | Reconcile the imported fragmentation source window, adjacent obligations and proposed requirement IDs into a reviewed ledger |
| [Architecture](architecture/REPORT.md) | Grid search correctness does not establish CSS placement correctness | Construct opportunities/geometry from a declared flow domain and prove the selected cut produces permitted fragments |
| [Evolution](evolution/REPORT.md) | A theorem can remain true while its applicability to current CSS becomes stale | Track a real cloned-decoration correction through requirement, model, observer and provider dependencies |

The coverage memo describes the inspected library inventory. Since that
assessment, root accepted the separate fragmentation rule/grid pilot after a
fresh replay. Its 34 audits do not close the family gaps in that table: CSS
sufficiency, emergency region, actual layout inputs and observers remain open.
See [root review](../css-fragmentation-unforced-root-v1/REVIEW.md).

## Sequence to implement

1. **Interpretation and accounting:** review the 174-unit fragmentation target
   and its adjacent dependencies; retain unresolved wording, CSS2 residuals and
   host dependencies explicitly. A validator can detect stale or missing links;
   independent review must decide whether the requirement inventory is complete.
2. **One constructed input bridge:** resolve the relevant sufficiency/region
   questions before implementation. Derive break classes, ancestry, continuation
   line counts and candidate geometry for a useful declared domain. Prove the
   actual selected cut's materialization, not only existence of some placement.
3. **Two consumers:** share fragments between restricted paint and ordered CSSOM
   observations. Challenge missing zero-sized fragments and incorrect glyph
   ownership even when a bounding rectangle is unchanged.
4. **Persistent histories:** add font/resource and scroll-sampling changes with
   explicit phase contracts. Do not replace prescribed sampling with a generic
   repeat-until-stable loop.
5. **Expand the versioned universe:** reconcile official module catalogs,
   surviving older clauses, media/roles and normative dependencies. Broaden
   implementation only with tracked requirement and integration obligations.

The maintenance example distinguishes a documented spec correction from a
literal old-text interpretation. Its ten passing structural/arithmetic checks
validate only the supplied example graph and contracts. They do not discover
missing dependencies or interpret CSS automatically.

## Standalone artifact and completion criteria

Keep specification relations, executable reference algorithms and optional
Gecko adapters separate within a portable repository. Release explicit partial
profiles while retaining the whole-CSS backlog. The three assurance claims are
separate: faithful normative model, proved executable reference and actual
engine refinement. All applicable requirements and transitive obligations must
close at the claimed tier before calling that tier complete.

Measure interpretation, proof, provider and integration/review work, reopened
assumptions and spec-change fan-out before estimating throughput. More Lean
lines, theorem declarations or passing browser cases cannot substitute for
those measurements or the normative denominator.
