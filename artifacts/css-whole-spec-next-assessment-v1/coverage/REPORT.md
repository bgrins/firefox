# What would make “all CSS” coverage auditable?

Research assessment, 19 October2026. **Recommendation: finish one requirement ledger against the source importer that now exists, and use it to drive expansion.** Another theorem total or architecture sketch would not resolve the current bottleneck.

## 1. Define the whole target without silently shrinking it

Use a versioned **normative universe**, with two named views: the dated stable Snapshot baseline and a reconciled current-draft view. The latter includes every CSS-family module in the official catalogs plus CSS-facing Houdini/FXTF/Web Animations APIs and the external contracts those modules invoke. Every catalog entry receives a disposition: selected, superseded with residuals, historical-only, unresolved/conflicting, or unrelated with justification. No desktop-popularity filter.

The [22June2026 Snapshot](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/) is a useful stable catalog, not an executable specification or a statement of browser adoption. A highest-level-only policy is wrong: its Box Model3 replacement explicitly retains CSS2 margin collapsing. Current draft diffs and inherited generic rules also require clause-level composition. Older inconsistent editions become separate versioned theories, not simultaneous requirements.

Keep print, speech, specialized media and role-specific conformance in the master universe. The [draft catalog](https://drafts.csswg.org/) still lists Speech and Paged Media; the [current-work index](https://www.w3.org/Style/CSS/current-work) also lists Houdini/FXTF work. A model may parameterize renderer/stylesheet/authoring-tool roles and allowed UA policies; it must record their obligations. This does not require one browser to act as every kind of tool. Unsupported optional branches can satisfy a particular implementation profile only when the spec allows it; their semantics remain uncovered in the whole-language objective. Device choices are constrained inputs, not permission to accept any output.

## 2. Current evidence is substantial but has no whole-spec denominator

Direct inspection of `css-spec-lean/coverage.json` finds127 historical feature records:120 `checked_fragment`,7 `unsupported`, and32 specification-version records. Its full-CSS, mechanized-prose-translation and browser-refinement flags are all false. These counts are **not requirements**. For example, the historical broad `raw-css-parsing` unsupported row coexists with later checked tokenizer/parser fragments; the rows overlap and cannot form a numerator/denominator.

The source-ledger pilot accounts for complete bytes of three acquired documents: Fragmentation3, one HTML semantics page, and Fonts4. It does not yet classify inherited normative context or interpret every clause. The earlier19-row sample marks all records uncertified; this does not invalidate its related Lean theorems. It records the missing source-to-requirement admission.

| Family / representative local evidence | Current evidence | Obligations still absent or conditional |
|---|---|---|
| Syntax and recovery: `CssTokenizer`, component/rule consumers | Scalar algorithms, independent relations, progress and finite streams; separate native tokenizer capsules | Encoding/byte admission and all public parser histories; general property/context dispatch and serialization composition |
| Selectors, namespaces, scope | Finite forest matching, specificity, broad supported source profiles, raw-scope fragments | Full dynamic/UI states, shadow/featureless/pseudo elements, namespace acquisition, all validity/recovery rules |
| Cascade, imports, variables | Source-derived author/layer/scope/import histories; versioned Variables1 and guarded Variables2 models | Full origin/host/Fetch mutation histories, substitutions with metadata, registrations and complete property interactions |
| Values/math/property computation | Typed calculations, exact rational/signed-zero fragments, staged supplied environments; visibility/opacity profiles | Complete property/descriptor registry, numerical policy and rounding, actual font/viewport/layout environment admission |
| Queries and containment | Global conditions, name-only container ancestors and supplied truth profiles | Size/style/scroll query semantics, temporal feedback and full containment/layout relationships |
| Box construction and layout | Library explicitly marks broad layout/rendering unsupported; separate local native repair proofs exist | Anonymous/generated/replaced boxes, intrinsic sizing, block/inline/float/position/flex/grid/table algorithms and joins |
| Fragmentation/print | Source accounting and proposed interpretation frontier | Reviewed break relation, progress/relaxation, varying fragmentainers, paged rules and decoration behavior; no complete executable family established |
| Fonts/text/writing modes | Separate local hyphenation, glyph/provider/cache work; Fonts4 source inventory | Full font selection/loading, shaping/bidi/ruby/spacing, logical axes, break selection and layout composition |
| Paint/images/color/effects | Opacity-only library fragment; static audits elsewhere | Color spaces, gradients/images, stacking, transforms, clipping/masking/filtering/compositing, rendering observations |
| Animation/temporal behavior | Generic `TransitionMachine.run_iff`; separate conditional native metadata models | Actual CSS timing/effect/transition histories, resource events, scroll sampling, notification/delivery and host progress |
| CSSOM/host/UI/security | Bounded source/DOM acquisitions and selected native fixes | Full object/serialization/live-read contracts, HTML style updates, DOM/flat trees, SVG, CSP/Fetch and user/device state |
| Speech/other media and conformance | Catalogued in primary sources; no corresponding library implementation identified | Media-specific semantics and role/policy obligations; cannot count screen-only closure as whole CSS |

“Absent” here means not established by the inspected library inventory, not a claim that no relevant theorem exists anywhere in the large artifact tree. Separate bug capsules require explicit import and contract review. `TransitionMachine` takes an arbitrary transition relation and per-step correspondence premise: its name must not be credited as CSS Transitions semantics. `Style.compute_sound` composes its supplied finite-forest/value profile; it does not construct a complete layout tree.

## 3. A denominator that survives proof production

Use two independently reviewable layers:

1. **Source-region accounting:** every selected document region has a disposition, including grammar, equations, table cells, figures, exceptions, normative advisements and informative material. Current lexical byte accounting is the input to this layer, not its completion.
2. **Requirement revisions:** stable semantic IDs attach interpreted obligations to those regions, roles, media, guards, errors, choices and observations. Generic requirements link their full instantiation registry. A requirement can span several paragraphs; a paragraph can support several requirements.

Do not let splitting one requirement into ten improve reported completion. Maintain a stable parent obligation and split/merge history; parent closure requires all children and integration edges. A supersession edge needs source and destination clauses plus residual exceptions. No silently dropped CSS2 section. Every unresolved normative dependency remains an open frontier even when its provider is supplied as a function to Lean.

### Concrete schema delta to implement

The prior inventory already proposes files; these are the crucial fields and constraints that the implementation must add to the present byte ledger:

```text
DocumentRevision(id, sourceHash, sourceRevision, status, catalogMembership)
UniverseView(id, selectedRevisions, roles, media, policyDomains)
SourceDisposition(unitIds, kind, normativeContext, reviewer, requirementIds)
Requirement(id, revision, parent, statement, guards, errors, observations,
            roles, media, choices, sourceBindings, interpretationStatus)
Dependency(fromReqRev, toReqRev, kind, dischargeOwner, status)
Replacement(oldRegion, newRegion, relation, residualRegions, review)
Claim(reqRev, tier, domain, declarations, assumptions, sourceVersion,
      replayReceipt, independentReview, status)
Instantiation(genericReqRev, registryRevision, member, discharge)
```

`Claim.tier` has **source-accounted / interpreted / proved-semantics / executable-reference / Gecko-refinement**. These are separate fields/claims, not one automatic staircase. An executable implementation can lack a soundness proof; a semantic theorem can lack executable realization. Native binding is not verified translation. A current source hash cannot revive a theorem for an obsolete interpretation. Include `refuted`, `stale`, `ambiguous`, `conditional` and `not-modeled` states; an opaque unsupported sentinel is not a permitted CSS outcome unless the requirement says so.

Example: a fragmentation progress obligation binds the exact acquired prose and adjacent relaxation rules. Its current source accounting may be complete while interpretation is proposed, semantics/executable/refinement are absent, and dependencies include break-class definitions and content/fragment identity. The class-B text/class-A-link contradiction retained by the importer must stay ambiguous; neither a valid anchor nor a successful Lean proof resolves it.

## 4. Smallest next deliverable

**Produce `requirements-pilot-v1` for the already imported fragmentation context, without acquiring another large proof corpus.** This is the missing next step after the source-ledger implementation:

1. Two independent readers classify all174 retained target-window units and explicitly include or cross-reference adjacent `best-breaks`, possible-break classes and forced-break interaction. They reconcile the existing13 candidate obligations;13 is a proposal count, not an acceptance target.
2. Record stable requirement revisions, scope/choices, exact source-unit links and open dependencies. Retain the text/link conflict as an issue; unrelated clauses can proceed. Bind the zero-size/progress and fallback requirements even if no outgoing hyperlink discovers them.
3. Implement a small validator that rejects orphan normative units, missing generic instances, unresolved references falsely marked closed, dropped residuals and stale proof links. Reuse the existing lock/importer; do not invent another source-acquisition framework.
4. Publish a plain dashboard showing interpreted/unresolved/absent states at each tier. Link any exact existing Lean result only after checking its proposition and premises; explicitly empty proof links are a valid first outcome.
5. Independently omit one adjacent obligation and alter one source clause. The accounting/interpretation review must detect the omission, and revision handling must reopen dependent claims. Merely accepting a newly regenerated byte ledger fails this gate.

This small pilot makes a future completion claim auditable because it tests omission detection, semantic granularity and dependency closure on an awkward real module. It **does not establish the global universe**. The immediate next inventory batch must reconcile Snapshot/current-work/draft/adjacent catalogs into an explicit roster and CSS2 residual map; then repeat the pilot on the already imported font-cluster and HTML style-update contexts. Those expose provider and temporal dependencies that fragmentation alone cannot validate.

## 5. What to report instead of a CSS percentage

Report named universe revision and unresolved catalog entries; unclassified source regions by family; reviewed requirement-parent states by tier; open imported contracts and cross-family joins; stale/refuted/ambiguous claims. Once a denominator is independently frozen, a count can describe bookkeeping progress, but does not measure equal semantic effort. A family is complete only when every applicable requirement and its required joins close at the claimed tier. No theorem count, source-byte total, WPT count or successful native matrix supplies that condition.

Whole-CSS semantic completion means the selected universe is accounted for and interpreted, every applicable obligation has a faithful proved relation with nonvacuous admitted behavior, and external assumptions are enumerated and discharged or explicitly make the claim conditional. Executable completeness adds realization/progress. Gecko completeness adds actual source/representation/caller/provider/history refinement across Stylo, layout, graphics and DOM. These are three different eventual products.

## Inspection and uncertainty

Read the v5 architecture, source-ledger report/frontier/scaling, prior inventory and worked slice, current coverage map/JSON, and representative Style/TransitionMachine definitions. No Lean or browser replay was performed. Family gaps are inventory-based; the complete artifact archive and all normative documents were not rereviewed. Primary catalog claims were freshly checked on19October2026 through web retrieval; SOURCES.json records URLs and local file hashes. No exhaustive current catalog count, completion percentage or timeline is claimed. This memo adds an implementation decision and schema constraints, not another accepted formal component.
