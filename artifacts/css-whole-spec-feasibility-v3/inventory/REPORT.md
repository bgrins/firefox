# What a complete normative CSS inventory must account for

Research date: 2026-10-19. This extends the two earlier inventories with a
concrete ledger stress test across layout, fonts, color, and HTML integration.
It does not inventory all CSS or establish new Lean or engine correctness.
The whole-CSS objective remains; views and pilots are intermediate artifacts.

## 1. A catalog is necessary but is not a normative theory

Use the dated [CSS Snapshot 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/)
as one authoritative root. It explicitly describes stability rather than
adoption, is not a desktop-browser-only profile, and includes scoped replacement
of CSS2 material. It is not a claim that all current drafts can simply be united.
For example, its Box 3 replacement leaves CSS2 section 8.3.1 intact. The sample
records that retained obligation without pretending to have translated it.

The [CSS current-work catalog](https://www.w3.org/Style/CSS/current-work) also
contains rewriting and abandoned work, and separately lists related
specifications. A repository directory, an abandoned profile, and a normative
module are different inventory objects. Keep all discovered objects, with
reasons for their disposition; do not silently discard experiments or elevate
every abandoned document into an active requirement.

I recommend three versioned layers:

1. **Discovery universe:** every candidate document, historical branch,
   normative dependency, relevant host integration, registry, and unresolved
   inclusion question. Multiple catalogs independently seed this universe.
2. **Source-accounted corpus:** exact document bytes and classifications for
   every included source unit, with unresolved material explicitly visible.
3. **Coherent normative views:** selected revisions and role/medium/feature
   predicates, scoped override edges, and an explicit conflict register.

“All CSS” means eventual coverage of this entire reconciled family, including
applicable print, speech, historical compatibility, and host requirements.
It does not require simultaneously asserting conflicting revisions. The final
model should expose their versions and applicability rather than choose one
silently. No known catalog alone supplies a proof that the universe is complete.

The [browser-specs registry](https://github.com/w3c/browser-specs) already has
useful series composition, obsolescence, release/nightly, and fork metadata.
Use those as discovery inputs, not clause-level supersession authority.
[Webref](https://github.com/w3c/webref) provides extracted definitions, CSS, IDL,
links, and back references. Its curated extracts exclude specifications outside
good standing, and its packages additionally restrict to browser-targeting
specifications. Consequently a curated CSS package cannot be the denominator
for the whole-CSS objective. Raw and curated inputs need separate identities
and any curation patches need provenance.

## 2. The missing denominator is semantic, not just documentary

The v2 requirement rows were useful examples, not a denominator. A paragraph
can impose several guarded obligations; a single generic rule can instantiate
over many properties; one behavior can require several modules. Conversely,
several paragraphs can specify the same obligation. Counting paragraphs,
properties, Lean declarations, tests, or files cannot identify completion.

Keep these separate:

| Inventory | What its denominator actually measures |
| --- | --- |
| Catalog reconciliation | Discovered entries with reviewed dispositions, including unresolved candidates |
| Source accounting | Units of the fixed corpus whose role has been classified; this can be mechanically exhaustive relative to the extraction partition |
| Semantic obligation ledger | Reviewed requirement families and their guarded instances in a theory view; granularity and interpretation remain reviewed choices |
| Model coverage | Obligations represented with appropriate inputs, outcomes, choices, errors, and temporal behavior |
| Proof coverage | Precisely stated properties of those models and their executable interpretations, with premises exposed |
| Engine conformance | Correspondence of a particular implementation and providers to the selected semantics at specified observations |

A mechanically complete source partition does not prove a complete semantic
translation. Report missing units and open interpretations alongside any
counts. Do not publish one blended percentage. When the ledger changes,
preserve stable obligation identities and explain splits/merges; otherwise
coverage can improve merely by changing granularity.

`ledger-schema.md` gives the proposed production records. Important additions
to v2 are role-indexed modality, choice persistence, guarded supersession
complements, generic instantiation registries, observation phase, and distinct
source-accounting versus semantic-closure status. Text predicates in this
prototype are proposals to formalize, not machine-interpreted conditions.

## 3. Worked cases that expose different failures

`sample-ledger.json` contains ten candidate rows. Each refers to an exact byte
range and hash within a retained full document. A range is the selected heading
through the next heading, not a claim to have classified every clause inside it.
All dependencies are open and all model/proof/engine bindings are absent.

### Flex distribution: grammar extraction cannot capture an algorithm

The [flexible-length algorithm](https://drafts.csswg.org/css-flexbox-1/#resolve-flexible-lengths)
iteratively distributes space, clamps sizes, and freezes items according to
violations. The inventory must link its input sizing obligations and numeric
domain, preserve the loop's branches, and distinguish the explanatory progress
note from the steps it explains. A proof pilot should establish progress and
used-size agreement under those inputs. Parsing `flex` or proving a generic
terminating loop would leave the central requirement uncovered.

### Fragmentation: latitude has guards and residual obligations

[Breaking rules](https://drafts.csswg.org/css-break-3/#breaking-rules) distinguish
forced breaks, allowed unforced breaks, staged relaxation, and progress. The
[optimization section](https://drafts.csswg.org/css-break-3/#best-breaks) does not
require one unique plan. Separate mandatory constraints from recommendations
and permitted choices. The model target is an allowed-plan relation, with a
separate executable selection policy. It must not treat “avoid” as absolute
when the prescribed relaxation applies, or treat all choices as unconstrained.
The three sample rows deliberately remain distinct.

### Font matching: external data does not make CSS decisions external

[Fonts 4](https://drafts.csswg.org/css-fonts-4/#font-style-matching) constrains
tie choices across elements in a document. Its
[cluster rules](https://drafts.csswg.org/css-fonts-4/#cluster-matching) distinguish
variation-selector fallback from optional other cluster fallback. Thus the
ledger needs persistent choice scope and branch-specific modality. Font
availability, support, Unicode clustering and canonical equivalence are named
provider contracts; the prescribed ordering remains a CSS obligation. A
per-call nondeterministic choice would lose the document consistency rule.
This is a concrete interpretation challenge beyond storing “UA-dependent”.

### Color: presence information and host context survive parsing

[Missing-component interpolation](https://drafts.csswg.org/css-color-4/#interpolation-missing)
preserves analogous missing components through conversion; the surrounding
interpolation algorithm orders conversion, missing-value treatment, hue
handling and premultiplication. A ledger that equates missing components with
numeric zero loses an observable distinction. The sample names conversion,
host interpolation-space selection and alpha treatment as open dependencies.
The first model should retain optional components and phase boundaries before
attempting numeric approximation proofs. This row does not cover all color
spaces, gamut mapping, rendering or compositing.

### HTML: incoming integration and conformance role change the inventory

[Updating a style block](https://html.spec.whatwg.org/multipage/semantics.html#update-a-style-block)
has connection/parser/children-change triggers and ordered stylesheet removal,
guards and creation. A CSS-only outgoing-reference crawl can miss the host
trigger obligation. Separate HTML author conformance from UA processing.

The [HTML rendering chapter](https://html.spec.whatwg.org/multipage/rendering.html#rendering)
also makes an unusually useful stress case: its suggestions become mandatory
for UAs designated as supporting suggested default rendering. A global
keyword-based classifier would misclassify it. The sample stores the role
guard explicitly, and leaves the role's defining contract open.

## 4. Explicit omission audit

This is a gap inventory, not evidence that the following surfaces have been
fully examined. Only the documents in `source-lock.json` were acquired here.

| Surface still needing full inventory | Failure to guard against | Required next evidence |
| --- | --- | --- |
| Complete catalog and every Snapshot tier | Missing non-browser/obsolete/experimental entries, or silently treating them as active | Pinned catalog union, reconciliation diff, every entry disposition |
| Module supersession and errata | Losing retained CSS2 rules; merging incompatible levels | Clause/domain override graph, overlap and residual audit |
| Property/descriptors/pseudos/at-rule registries | Generic rules fail to cover newly added or exceptional members | Versioned domains, eligibility predicates, generated instances and exception review |
| Prose, algorithms, tables and figures | Grammar/IDL extraction misses layout equations or negative requirements | DOM source partition, inherited normative context, tables/figures/captions inspected |
| CSSOM, Typed OM, animation APIs | Correct static values but wrong observable mutation/getter history | API, exception, serialization and temporal requirement families |
| HTML, SVG, DOM, shadow/flat trees | Missing incoming callers and host lifecycle | Reverse-link audit plus manually enumerated trigger/observer graph |
| Fetch, URL, CSP, encoding, security/privacy | Modeling a resource as available without required loading or access decisions | Narrow imported contracts and complete CSS-owned call obligations |
| Fonts, Unicode, shaping, media/device inputs | An opaque provider hides CSS decisions or required data versions | Operation-level provider schema, version policy, data interpretation obligations |
| Layout, fragmentation, writing modes, text | A handful of algorithm rows replaces the full geometry system | Cross-module input/output and ordering graph; every applicable mode |
| Paint, SVG effects, compositing, hit testing | A geometry model is mislabeled rendering conformance | Distinct output observations, numeric/approximation and host contracts |
| Print, speech, accessibility, forced preferences | Desktop visual scope accidentally becomes final scope | Role/medium matrix and explicit retained obligations |
| Undefined/unspecified/optional/implementation-defined cases | One undifferentiated escape hatch permits arbitrary behavior | Per-case permissions, persistence, constraints and unresolved interpretations |
| Cross-module composition and dynamic changes | Each local row closes while the composed state is stale | Interaction obligations, scheduler/readiness observations and dependency invalidation |

This sample does not retrieve CSS2's retained margin section, the referenced
Unicode standards, CSP, or every color provider. They are explicitly open,
not authenticated merely because their referring document was retained.
It also does not decide current browser support, WPT adequacy, historical
novelty, or any implementation defect. No browser or native code was run.

## 5. Practical extraction and validation plan

1. **Acquire and reconcile.** Pin full HTML plus authoring-source revision when
   available; record redirects, fetch time, edition and extraction version.
   Retain raw catalogs and compare their memberships. A transient fetch failure
   creates an open entry, never an automatic exclusion. This sample pins content
   hashes and fetch metadata; it does not have upstream Git commits for drafts.
2. **Partition before translating.** Account for every content node under a
   fixed partition policy, including nested list steps, table cells and external
   figures. Preserve inherited normative/informative context. Examples and
   change histories can help interpretation but must not silently override the
   normative body. Detect uncovered and multiply classified source units.
3. **Extract candidate requirements with context.** Use prose/grammar/IDL and
   reference tools together. Preserve outer guards and subject roles. Agents
   should propose modality, quantification, provider and temporal edges, and
   mark uncertainty. Do not use modal-keyword search as the completeness test.
4. **Review source-to-ledger independently.** Have a second reader classify a
   section without seeing the first extraction, reconcile disagreements, and
   challenge every catch-all/provider clause. Check branch and error cases,
   permitted behaviors, negative obligations, and generic instantiations.
5. **Close interactions before claiming semantics.** Walk outgoing and incoming
   calls, type/unit conversions, host triggers and observers. Add explicit
   interaction requirements where no single paragraph describes composition.
   Test relation nonemptiness and contradictory guards; a relation admitting
   no behavior is not a satisfactory formalization.
6. **Bind Lean and executable/native results separately.** Link the exact
   theorem statement, supported input domain, premises and observation relation.
   A proved conditional theorem with an unbridged provider remains conditional.
   WPT can challenge an interpretation but cannot certify the denominator.
7. **Make updates invalidate claims.** Changed sources require span and semantic
   re-review; changed registries require generic-instance checks; changed host
   contracts invalidate dependent closures. Do not silently move a proof to a
   new anchor or a newer draft. Resolutions and issues are interpretation evidence
   until their status relative to the selected normative edition is recorded.

For agent parallelism, assign source partitions plus shared-definition owners;
do not split solely by property names. Require each handoff to list incoming
dependencies, outgoing obligations, unresolved interpretation and residual
source units. A separate integration reader owns theory-view consistency.

## 6. Concrete next deliverable

Implement the production catalog/partition validator first, using the schema
here and v2's file layout. Then fully account for three deliberately different
small sections: flex distribution, fragmentation break rules, and HTML style
block update. Each must include its dependency frontier and conformance roles.
Keep the prior custom-property/CSSOM pilot as the fourth comparison, not the
definition of all CSS. These pilots test whether the ledger survives algorithms,
constrained choices and host-driven state before expanding across every module.

`validate.py` currently checks source hashes and selected spans, the exact
sample roster, required dependency presence, guarded modality/choice fields
against the proposed review shape, and prohibition of unsupported coverage
claims. Ten deliberately corrupted ledgers are rejected. `reviewed-shape.json`
is an author-supplied proposed interpretation, **not independent approval**.
These are bookkeeping tests, not semantic mutation proofs. The validator does
not parse predicate meaning, prove prose equivalence, or check complete source
accounting. `prepare-sample.py` reproduces the sample data from the retained
bytes. There are no external Python dependencies.

Human interpretation remains essential for authority conflicts, implicit
conditions, diagrams, scoping a provider, deciding compatible UA choices,
choosing observation relations and numeric tolerances, and determining whether
the composed model expresses the intended requirement. Agents can make this
work systematic and reviewable; Lean cannot certify the translation merely
because the resulting definitions type-check.

## Reproduction and evidence

Run `python3 validate.py` from this directory or by absolute path. The saved
`VALIDATION.json` records the successful structural check. `source-lock.json`
contains ten complete primary-source files and their retrieval identities;
`web-browse-*.json` retains browsing discovery. `predecessor-inputs.json` records
the earlier reports consulted. The optional webspec-index helper remains absent
after the parent's earlier bootstrap attempt, so direct primary retrieval was
used. This introduces no new implementation or formal acceptance claim.
