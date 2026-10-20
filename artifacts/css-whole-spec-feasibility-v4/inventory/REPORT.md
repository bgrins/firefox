# A usable requirement ledger and honest completion gates

This pass implements the structure proposed in v3. It supplies executable
SQLite DDL (`schema.sql`), four source-bound stress cases plus explicit open
dependencies (`examples.json`), and a small gate demonstration (`demo.py`).
It is bookkeeping infrastructure, not a complete inventory or new CSS proof.

Run `python3 -I -S demo.py`. It creates only in-memory databases. `RESULT.json`
records the expected blocked CSS sample, a separately labeled synthetic
positive fixture, ten rejected structural challenges, and rejection of a native
claim backed only by model bindings. It needs only Python's standard library
with SQLite JSON support. No Firefox build or browser is involved.

## 1. Implemented records

| Tables | What they preserve |
| --- | --- |
| `document`, `catalog_entry`, `profile_document` | Exact edition/content identity; discovery origin; active/draft/obsolete/experimental status; selected, historical, dependency, and unresolved entries |
| `profile` | Explicit normative view, roles and revision; sample versus full-universe scope; separate universe/source/interaction review attestations |
| `source_unit`, `requirement_source` | Prose, algorithm, grammar, table, figure and IDL units; inherited normative context; many-to-many obligation mapping; unclassified remainder |
| `requirement`, `predicate` | Stable requirement revision, subject, modality, guarded domain, contract, and interpretation state |
| `semantic_interface` | Versioned semantic signature; phase, owner, environment/version dependencies and observation protocol belong here |
| `dependency` | Named semantic, provider, host, temporal, registry and premise edges; dependencies remain visible even when not top-level targets |
| `replacement`, `target` | Scoped replacement and retained residual; explicit decisions for historical or inapplicable material |
| `choice_contract`, `transition_contract` | Permitted relation, consistency/nonemptiness obligations and persistence; triggers, observation timing and readiness obligations |
| `binding` | Separate model/executable/native claims, pinned requirement/interface revisions, contract digest, observation ID and evidence reference; unsupported/conditional/stale are not accepted |

Guards have a small Boolean syntax: `true`, `false`, named `atom`, `not`,
`all`, and `any`. A predicate names a semantic definition; its meaning is not
inferred from English. The demo checks shape, named predicate review, and
propositional satisfiability over at most ten atoms. This does not prove that
an environment realizing those atoms exists.

The binding digest includes the requirement, linked source-unit records and
document hashes, and interface record. Editing any of those makes the old
binding stale. The ledger must also track dependency evidence revisions in the
production certificate graph; the demo traverses dependencies and rechecks
their current bindings, but does not implement persistent proof invalidation.

The semantic track's proposed IDs—`css.core.request-trace.v1`,
`css.layout.size-request.v1`, and `css.animation.sample-request.v1`—are recorded
as **proposed**, with no claimed normative binding. Intrinsic/used/sample phase
distinctions and geometry/sampled-effect observations should not be flattened
when those interfaces are integrated.

## 2. Acceptance criteria for “all CSS”

The global target remains the entirety of CSS. A finite release must name the
edition family it covers, including current selected drafts, surviving older
rules and host integrations. Profiles manage conflicting versions; they must
not silently remove unsupported features from the final objective.

The dated [CSS Snapshot 2026](https://www.w3.org/TR/2026/NOTE-css-2026-20260622/)
provides an authoritative starting profile and identifies scoped supersession,
not a license to equate browser adoption with scope. Keep the current-work and
adjacent-spec reconciliation from v3. Historical/experimental entries remain
cataloged with reviewed dispositions; historical compatibility rules that are
still active remain target requirements.

Completion needs all of the following, with separate conclusions:

1. **Inventory acceptance:** reconciled catalog sources and exact revision
   selection; exhaustive source-unit partition; reviewed requirement extraction;
   resolved exclusions, overrides, residuals and conflicts; incoming host
   obligations; complete generic-rule instantiation domains. A missing module
   cannot be excused by absence from the hand-written requirement table.
2. **Specification-model acceptance:** every applicable requirement has faithful
   semantics, including errors, permitted choices, unsupported implementation
   domains, timing and observers; dependencies close at the model level;
   admitted inputs and permitted behavior are nonvacuous. UA latitude is a
   constrained relation, not an arbitrary-answer provider.
3. **Executable-reference acceptance:** a specific implementation of those
   semantics has proved soundness, stated completeness/choice-policy guarantees,
   progress where required, and numerical contracts. A reference returning
   `Unsupported` for a target domain has not completed that domain.
4. **Engine acceptance:** source, representation, provider, arithmetic,
   scheduling and observation correspondence additionally close for a particular
   engine version. A specification model or executable theorem cannot stand in
   for these obligations.

These are different claims. No theorem/file/property count establishes any
one of them. The schema can record their evidence but cannot confer authority
on a string labeled `accepted`.

## 3. Stress cases and concrete failure modes

### Box model: replacing a section while retaining its exception

Snapshot's Box 3 entry replaces selected CSS2 box sections while retaining
8.3.1. The example records a replacement predicate and its residual separately,
with the retained requirement active. The CSS2/Box3 semantic sources remain
explicitly unacquired in this pilot. Deleting a required residual blocks the
synthetic gate; declaring the partition accepted still requires independent
proof/review that it exhausts the old domain without overlap. A highest-level
module selector cannot perform this step.

### Fragmentation: constrained choices and progress

[Unforced breaking](https://drafts.csswg.org/css-break-3/#unforced-breaks)
includes staged relaxation and progress constraints. The example adds a choice
record with named consistency and nonemptiness obligations. Both stay open;
their mere names prove nothing. A single selected break plan may implement the
relation without defining its full permitted set. The checker requires
dependencies and rejects an ungrounded dependency cycle; supporting a genuine
recursive semantic component will require an explicit composition certificate,
not simply changing a cycle's status to accepted.

### HTML stylesheet updates: events are part of the requirement

[Update a style block](https://html.spec.whatwg.org/multipage/semantics.html#update-a-style-block)
has parser/connection/children-change triggers and ordered effects. The sample
stores those triggers, stylesheet availability as the observation, and a named
readiness contract. A proof for a precomputed stylesheet cannot close this
transition. Dropping an observer or substituting pixels for CSSOM state must
invalidate the binding. Renaming the entire observer contract consistently can
still hide an omission; an independently reviewed observer roster is necessary.

### Fonts and SVG: imported data versus CSS-owned decisions

[Font cluster matching](https://drafts.csswg.org/css-fonts-4/#cluster-matching)
references Unicode segmentation and canonical equivalence while prescribing
matching/fallback decisions. The sample retains open clustering, font support,
equivalence and fallback dependencies. Versioned font/Unicode contracts are
needed; “the font provider supplies the correct result” cannot close them.

[SVG presentation attributes](https://www.w3.org/TR/SVG2/styling.html#PresentationAttributes)
use CSS-value parsing and have cascade and element-applicability rules, including
a property/element table. SVG is therefore an explicit unresolved catalog
dependency here. A CSS property grammar inventory alone would omit this host
mapping. The table's exceptions need their own source units and requirement
instances; this pilot does not claim to have extracted them.

## 4. What the demonstration actually catches

The tests reject an unsupported transitive provider, changed or missing
interface, observation mismatch, syntactically false domain, unfounded cycle,
unexplained replacement, unproved exclusion, changed contract, and lost
residual. Model bindings alone also fail the executable/native levels. SQL
constraints enforce referenced identities, allowed states and required fields.

The positive case is a synthetic two-requirement dependency graph with asserted
review/evidence fields. It tests that the structural gate is not constant
failure. It is deliberately not a CSS acceptance example. The real stress-case
database fails, as it should: candidate interpretations, unclassified remainder,
missing sources and provider obligations remain.

The following are **not** established by `demo.py`:

- Completeness of the input catalogs or source partition, source byte validation,
  semantic completeness of a coarse requirement, or validity of an exclusion.
- Meaning of free-form contract JSON, truth of review attestations, authenticity
  or kernel checking of evidence references, actual inhabitedness, or permitted
  behavior beyond the Boolean guard check.
- Exact complement/overlap of replacement domains, generic registry coverage,
  a certified dependency-cycle composition, or dynamic trigger exhaustiveness.
- Faithful imported HTML/SVG/Unicode/font behavior, current engine support,
  native execution, or browser conformance.

These are implementation and interpretation obligations, not exclusions from
the whole-CSS goal. In particular, partitioning all source bytes can still
miss an exception semantically, and a vacuous executable can still type-check.

## 5. Practical first milestone

Turn this schema into a checked catalog/partition importer and use it to fully
account for **one section in each of three families**: fragmentation break
rules, HTML style-block updates, and font cluster matching. Keep their entire
dependency frontier visible; this is a milestone, not the final scope.

Acceptance for that milestone:

- Pin complete sources; independently reconcile discovery lists and fetch
  failures; generate a deterministic partition covering all content nodes,
  including normative tables/algorithms and informative classifications.
- Two readers independently extract requirements and reconcile guards,
  exceptions, observer lists and external contracts. Retain disagreements.
- Validate exact byte spans, immutable contract revisions, source accounting,
  missing edges, stale evidence and requirement/observer identity changes.
- Connect real Lean declarations and proof receipts for selected obligations;
  leave everything else open. Add actual certificate verification and a
  dependency/SCC composition protocol before using a release gate.
- Replay a spec edit that changes an exception or host trigger and show that
  the affected binding and dependent release claim become stale.

Automation can acquire, partition, reconcile, enforce schemas, discover links,
compute dependency frontiers and detect stale identities. Agents can propose
extractions and challenge alternatives. Experts still decide normative meaning,
authority, exception scope, allowed policies, imported guarantees and observation
completeness. Those decisions must become reviewable inputs rather than remain
implicit in implementation code.

Sources were rechecked through primary web retrieval. `SOURCE-NOTES.json` reuses
the four exact full-document hashes and selected spans retained by v3; the demo
does not require or revalidate those HTML files. `web-evidence.json` retains
the new retrieval results, including SVG. No new semantic completion claim is
made by this research artifact.
