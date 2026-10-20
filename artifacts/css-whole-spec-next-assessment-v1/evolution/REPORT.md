# Operating a CSS-to-Lean artifact alongside living specifications

Research recommendation. Extends architecture-v5, the source-ledger scaling report and v4 validation; it does not replace their whole-CSS scope. The new contribution is a model-connected change exercise and concrete release/measurement rules. No new CSS proof, browser run or native change is claimed.

## 1. Preserve three different claims through every change

A normative model claims that its allowed behaviors faithfully express a selected source profile. An executable reference claims that its algorithm implements that relation on a declared domain. An engine adapter claims correspondence for particular source, representations, providers and observations. Keep those claim records separate and immutable per release.

Kernel replay establishes the checked proposition, not its interpretation as CSS. Lean's own validation guidance calls for checking statements and assumptions as well as proof validation. [Lean proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

A source edit therefore changes *claim applicability* before it necessarily changes theorem truth. Mark affected current-profile claims stale; keep old-profile proofs valid under their old names. Restore them only with an interpretation decision, updated dependency/observer contract and appropriate proof transfer. If a permitted-outcome relation grows, an old deterministic reference may remain sound through a proved inclusion; a claim that the old model describes **all** permitted behavior does not follow. Record which implication is transferred.

## 2. Concrete change exercise: cloned decorations

The [2018 Fragmentation CR](https://www.w3.org/TR/2018/CR-css-break-3-20181204/#unforced-breaks) repeats end-side truncation in the second fallback. The [pinned Editor’s Draft](https://drafts.csswg.org/css-break-3/#unforced-breaks) instead adds start-side truncation. The retained source identities are in `change-case.json`. The current draft’s [change log](https://drafts.csswg.org/css-break-3/#changes) explicitly identifies the older reference as a mistake and links CSSWG issue5070. That supplies an authoritative correction disposition. A dated profile still needs an explicit policy for incorporating this correction; silently rewriting its retained bytes would destroy reproducibility.

The now independently reviewed grid pilot has an actual distinguishing input: prefix extent2, cloned start1/end2, capacity2. End-only removal leaves extent3; removing both sides leaves2. Its `both_clone_inhabited` witness reaches the final ordinary stage. Repeating end-only removal would leave this prefix unfit. This is an exact-grid interpretation discriminator, not evidence of older-browser nonconformance.

A maintenance workflow should:

1. Preserve both document locks and the old release. Associate stable requirement identity `UB-truncate-start` with a new source binding; do not identify a requirement solely by a hash-dependent lexical-unit ID.
2. Record the change-log-backed correction and the reviewer’s decision about which profiles incorporate it. Retain the literal-old arithmetic outcome as a counterinterpretation, not as an endorsed CSS requirement.
3. Mark decoration extent, grid placement, stage selection and consuming fragment observations stale. Do not invalidate unrelated typed-avoidance facts solely because the document changed; require explicit unchanged-binding review before reusing them.
4. Review the source relation before changing the executable model. Re-establish stage ordering and distinguish ordinary from cloned decoration. Check the common-decoration-list admission against every candidate prefix.
5. Keep CSS sufficiency, continuation/layout inputs and emergency-region obligations open. A new source hash and passing grid proof cannot close them.
6. Publish which old proofs were replayed, transferred through a semantic bridge, replaced, or left conditional. Engine claims require a separate source/provider/runtime gate.

`acceptance_examples.py` runs ten structural/arithmetic examples: old-profile staleness, changed-label/old-binding rejection, dropped observer/assumption rejection, unresolved-interpretation rejection, model-to-native promotion rejection, transitive invalidation, and the two prefix outcomes. It ran successfully (`RESULT.json`). It is a small proposed policy demo. The graph, review state and required observers are supplied inputs; the script cannot certify that those inputs exhaust CSS.

## 3. Faithfulness and omission detection must be review work products

Use a compact interpretation card for each requirement cluster: source/profile, conformance role, domain and triggers, required/allowed/forbidden outcomes, exceptions and priorities, observable history, external providers, unresolved alternatives, and distinguishing scenarios. Two readers should derive cards independently before seeing generated Lean; reconcile differences explicitly. A second proof of the same mistaken classifier does not supply independent interpretation.

Run omission reviews in both directions:

- **Source→model:** every normative paragraph, table, algorithm branch and relevant adjacent dependency receives a disposition. The fragmentation pilot needed the adjacent zero-size rule despite a complete target-section inventory.
- **Observer→source:** select a public read/write/event/render trace and walk backward through its providers. This catches omitted CSSOM, URL eligibility, selection/hit testing, resource and update behavior that a property grammar or screenshot suite can miss.
- **Exception→witness:** require an admitted example and a rejected nearby example for each interpretation boundary. The fragmentation emergency-region alternatives both satisfy weak structural admission yet select different outcomes; that is an open interpretation, not a choice for the proof producer to conceal.
- **Assumption→caller:** identify where each assumption becomes true and remains true. The independent forced-break challenge demonstrates that ordinary cut filtering alone does not establish global forced-event exclusion.

Allowed UA variability belongs in a relation with realizable, history-consistent choices. A deterministic reference may select one policy. Unresolved wording is a different status; do not encode it as unrestricted UA freedom. External fonts/resources may be inputs, but CSS selection, dependency tracking and observable response to their changes remain obligations. Explicit unsupported domains stay in the whole-CSS backlog; they are not invalid CSS inputs.

## 4. Minimal operational mechanism

Extend the existing ledger rather than create another proof-capsule framework. A release claim should bind:

```
claim ID + tier
profile / requirement revision / interpretation revision
model interface and theorem statement digests
required observation/history contract
provider assumptions and their current discharge status
source/refinement dependencies
review decisions + replay receipts
```

The proposed standalone release must replay its core without a Gecko checkout, browser or network once pinned toolchain/dependencies are supplied; keep source licenses/provenance and optional engine adapters separate. A document watcher should create review tasks, not automatically publish new semantic claims.

Source fetching and diffs create review tasks. Content/anchor/grammar/link changes conservatively stale their bindings; a reviewer decides semantic continuity. Follow the *semantic* dependency graph as well as Lean imports: downstream observers, host triggers and providers can depend on a concept without importing its module. Missing graph edges are themselves reviewed requirements. Strongly connected dependencies need a joint contract/proof; mutually assuming the other side is correct is insufficient.

Use states such as `uninterpreted → proposed → reviewed-conditional → discharged`, with separate `stale`, `ambiguous` and `unsupported` dispositions. Transitions require named evidence. Never let a regenerated source lock, a theorem count or a green compile directly move a requirement to discharged.

## 5. What exists versus what remains proposed

| Existing implemented evidence | Still proposed/open |
|---|---|
| Source-lock/lexical accounting importer with corruption controls and exact section slices | Whole normative universe, semantic clause completeness and maintained supersession/host closure |
| Fragmentation rule/grid equivalences, finite witnesses and independent replay | CSS sufficiency, real layout/continuation provider, exact emergency region, browser observations |
| Independent scope/assumption reviews and reproducible local proof receipts | A maintained semantic dependency/invalidation service and release authorization workflow |
| This ten-check migration demo | Correctness/completeness of its requirement/observer graph and expert review decisions |

The existing source ledger's document-qualified unit IDs invalidate broadly after edits. Stable semantic IDs with reviewed rebinding are a practical next step, not already implemented automatic semantic matching.

## 6. Agent organization and data needed before estimating coverage

Assign three roles per bounded component: independent interpretation/oracle; model/reference proof producer; integration/claim reviewer. Native adaptation is an optional fourth lane with its own acceptance. Keep one owner for shared interface changes. Rotate reviewers and preserve disagreement records. Limit active proof production to review capacity; a growing queue of unreviewed assumptions is not progress toward whole CSS.

Record the following per *accepted requirement cluster and interface change*, not per theorem:

| Measurement | Why it matters |
|---|---|
| Interpretation, proof, provider, integration and review effort separately; active versus queued time | Reveals the actual limiting role and useful parallelism |
| Initial review rejects, reopened decisions, time to resolution | Captures the cost hidden by first-pass proof generation |
| New versus reused interfaces; direct/transitive change fan-out | Distinguishes routine extensions from cross-family work |
| Provider obligations opened/discharged and unsupported-domain changes | Prevents apparent speed from exporting hard semantics into assumptions |
| Nonvacuous scenarios and deliberate semantic faults detected, with reviewer effort | Measures validation strength without treating finite tests as completeness |
| Source-change frequency, reviewed rebinding rate and stale-claim age | Measures the cost of keeping pace with specifications |
| Reproduction success, setup time and tool/source failure categories | Measures standalone usability separately from semantic assurance |

We currently have exact replay/audit/guard counts for small pilots, not a representative effort distribution across layout, text, painting and host histories. No full-coverage estimate is justified. Collect comparable observations across several dissimilar families and at least one real interface migration before estimating later batches, with uncertainty and review capacity explicit.

## 7. Next deliverables

1. **One maintained change card:** turn the decoration example into a reviewed correction/profile migration, retaining the literal source difference, correction evidence and every affected/unaffected decision. Exit: both profiles remain replayable; no new CSS claim is promoted from labels alone.
2. **One real provider closure:** implement and independently review a concrete continuation/opportunity provider for the accepted grid domain, including forced events, candidate-dependent decorations and zero boxes. Exit: a useful nonempty domain discharges a previously open admission, or a concrete counterexample forces interface revision.
3. **One observer-complete vertical release:** use the architecture report's registered-property provenance chain or a bounded host/layout history. Exit: independent source→model and observer→source reviews agree, counterexamples distinguish omitted metadata/events, and a fresh external consumer reconstructs the conditional claim.
4. **A small change/review dashboard:** report accepted, stale, ambiguous and unsupported requirements by family and tier, plus the measured workload above. Keep unresolved whole-CSS requirements visible; do not display a fabricated completion percentage.

These deliverables test whether new theorems retire real semantic obligations. They are more informative for the eventual whole-CSS objective than extending isolated theorem inventories.
