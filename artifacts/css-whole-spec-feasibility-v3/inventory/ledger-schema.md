# Proposed production ledger

This schema extends v2's file layout. `sample-ledger.json` is a small concrete
instance, not a completed inventory. Human-reviewed text fields remain text;
the prototype validator does not infer their meaning.

| Record | Required fields and invariants |
| --- | --- |
| Document revision | stable family ID; exact edition URL; fetched URL and time; content hash; upstream commit if available; status; publisher; source versus generated artifact identity; publication and editorial dates separately; retrieval failure status |
| Catalog membership | document revision; discovery catalog and version; entry; inclusion/disposition reason; role as specification, profile, explainer, registry, test, or historical document; independent reconciliation review |
| Theory view | versioned selected revisions; host and conformance roles; medium; optional modules; extension policy; unresolved conflicts; exclusions remain linked to the master universe |
| Source unit | document hash; byte range and hash; DOM ancestry and inherited normative status; heading/anchor aliases; unit kind; links; exactly one accounting disposition, potentially many requirement links |
| Requirement | persistent semantic ID; revision; subject/role; modality; quantified input domain; applicability predicate; observation phase; preconditions; outcome relation or transition; errors; temporal obligations; choice scope; dependency IDs; exact source spans; interpretation status/reviewer |
| Supersession edge | source and destination units/requirements; replaces/extends/amends/conflicts; explicit domain/guard; retained complement; authority; unresolved overlap. Never merely highest module number |
| Generic instantiation | generic rule ID; versioned property/descriptor/pseudo/etc. registry; eligibility predicate; exceptions; instance generation hash; new-entry obligation. Runtime custom names are quantified, not enumerated |
| External contract | consumed operations/data; version; guarantees; responsible model; CSS obligations retained locally; assumptions; evidence; unresolved provider correspondence |
| Choice contract | permitted set; mandatory constraints; policy owner; persistence scope (call/document/session/platform); dependencies; independent nonemptiness/consistency obligation. Permission does not mean arbitrary output |
| Coverage claim | requirement revision and view; model declaration; executable correspondence theorem; native correspondence theorem; exact premises; source/version binding; observation relation; proof receipt; review state. Each of these is independent and may be absent |
| Interpretation issue | exact conflicting/ambiguous spans; alternatives; consequences; provisional choice; CSSWG issue/resolution if checked; reviewer; expiration/recheck trigger |

Finite enum statuses: `unclassified`, `candidate`, `reviewed`, `blocked`,
`superseded`, `not-applicable-in-view`, `closed`. `Unsupported` in an executable
is never encoded as CSS invalidity. A source-accounting disposition is distinct
from semantic closure. `not-applicable-in-view` must name the failed predicate;
it does not remove the requirement from the master inventory.

For a complete model claim, every applicable reviewed requirement must have an
interpretation and connected semantics, every dependency must close, and all
conflicts and unclassified units must be resolved. An executable then requires
soundness plus the expressly claimed completeness/choice policy. An engine
claim additionally requires source/provider/representation correspondence.
None of those global gates is achieved by this sample.
