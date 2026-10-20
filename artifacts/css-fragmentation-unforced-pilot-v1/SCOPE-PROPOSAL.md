# Proposed first fragmentation semantic component

**For root interpretation/scope approval before implementation.** Source: exact CSS Break3 ED `57df3c079bf09547c05c1c0745b1ea1067344e88adaa844ec2e1ed1cde5faa82`. Independent thirteen-clause inventory and eight scenarios are copied unchanged. No Lean claim exists yet.

## Intended result

A source-bound relation of permitted next-fragment decisions, plus a finite executable selector proved to satisfy that relation. The selector implements one allowed choice policy; it will not claim CSS specifies a unique cut, optimal page balance or a particular avoidance score. Concrete source constructors and geometry calculations replace arbitrary predicates named after CSS rules.

The first model covers a restricted one-dimensional, finite, already laid-out flow, including the staged relaxation and emergency-progress structure of §4.4. Input admission from an HTML/CSS box tree, inline layout or Gecko remains open. The resulting theorem is an abstract semantic component, not an engine correctness theorem.

## Admitted data and source interpretation

- Ordered finite content identities with exact nonnegative integral grid extents; the grid scale is supplied and fixed. No real-number approximation theorem is claimed. Fixed positive fragment capacity, initially empty fragmentainers, and no floats, negative margins, parallel flows, forced blank pages or varying inline layout. This excludes the separate decision to move an intact block from a partly used fragmentainer.
- Explicit block/line identities and ancestor chains; A opportunities between admitted sibling boxes, B between lines of one block, C at admitted nonzero content-edge gaps. A finite boundary table is derived from these records. Completeness relative to real CSS opportunity generation is a named provider contract, not inferred from a list being finite. Monolithic interiors have no ordinary opportunities.
- Concrete break-value constructors (`auto`, general and type-specific avoidance, forced values), and a set of active break types. A break can have both page and column types; it is not modeled as one exclusive enum value. Applicable before/after controls and common/all-ancestor memberships are input records with an explicit cascade/propagation admission. Forced-break cases are classified and handed to an unresolved forced provider rather than treated as ordinary choices.
- Rule 1 computes applicable avoidance by break type. Rule 2 checks its actual all-auto antecedent and common-ancestor condition. B line-count conditions use independently recorded enclosing-block membership and derived counts. The exact meaning of counts for continuation fragments needs approval before a history theorem; the one-decision model must not silently reuse whole-original-block counts.
- **Rule 4 interpretation choice:** use the visible B/C wording, retain the class-A hyperlink inconsistency in the claim. Type-specific `break-inside` normalization must be explicitly reviewed. Initial strict support can be limited to `auto`/`avoid` ancestors while before/after tests exercise type-specific controls; unsupported ancestor values remain outside this initial admission, not proved equivalent to either value.
- Cloned start/end margins, border and padding contribute exact nonnegative extents derived from active box records. Ordinary decorations are separate and cannot be erased by the clone fallback. Box-model treatment of adjoining margins and already-truncated cloned margins remains an explicit provider admission; the model will not double-count them.

## Independent declarative relation

`AdmissibleNext input outcome` specifies source conditions directly, independently of the executable filter. Outcomes identify an end cursor, source content covered, ordinary/emergency status, chosen relaxation stage and the exact clone sides truncated.

Stages, in order: strict rules 1–4; drop rule 3; drop rules 1,2,4 as well; truncate cloned end sides; truncate cloned start sides too. An outcome at a later stage carries evidence that every earlier stage was geometrically insufficient. Merely having an allowed boundary does not establish sufficiency.

For the finite geometry model, a complete placement of the remaining content is feasible when its calculated extent fits. Otherwise a candidate placement is feasible when it consumes a positive content prefix, ends at an eligible opportunity, and its independently calculated extent with that stage's decoration treatment fits. Empty filtering alone is not a failure certificate: a boundary can be allowed but too far away. The certificate is universal absence of a feasible placement among the complete modeled boundary set, and the executable evaluator must be proved equivalent to that quantification.

**Interpretation boundary requiring approval:** equating this restricted local placement condition with §4.4's “sufficient break points” is not a proven general CSS fact. Initially empty, fixed-capacity fragmentainers and immutable laid-out geometry remove several alternatives, but do not by themselves resolve every continuation/ancestor case. If this cannot be justified for the proposed domain, return a named unresolved sufficiency result and prove only the rule/evaluator component; do not relabel it complete escalation semantics. This is the main interpretation gate before implementation.

Emergency choices require the final source guard: no ordinary possible point below the top in the relevant admitted region, and remaining content does not fit. The scope of “below the top” versus points beyond the current fragment's extent must be adjudicated explicitly. The selector may choose graphical slicing only under that guard, and may not emit a top break or an empty-progress fragment. Absence of a fitting legal point alone is not silently substituted for absence of a possible point.

## Executable selection and termination

Enumerate modeled boundaries in source order, compute the rule predicates, calculate placement extent from content/decorations, and choose one feasible member of the first sufficient stage. Preserve all earlier failure certificates. Avoidance weighting after relaxation remains optional; a simple deterministic source-order policy is a permitted implementation candidate only after relational soundness is proved.

Use a finite content cursor with an additional finite slice offset for monolithic graphic content represented on the admitted grid. Emergency creation must consume at least one positive slice unit; advancing only a zero-sized box will not justify that witness. Completion of all-zero content is separate and creates no repeated empty fragmentainers. A lexicographic remaining-content/slice measure gives termination of this finite selector/history, provided continuation contexts are admitted at each step. No inference from positive real progress to termination is allowed.

The adjacent `best-breaks` earlier-side zero-sized-fragment requirement must be enforced for fitted zero-sized records at a chosen cut. Its after-overflow exception remains explicit; it cannot be inferred from zero height alone. If the pilot only emits fitting prefixes/slices, an already-overflowing predecessor is outside its admission and the exception is a retained external scenario, not a passing test.

## Proposed proof and challenge gates

1. Derived class/ancestor/line-count rule checks equal an independent constructor-based declarative condition; branch nonemptiness and failing guards are explicit.
2. Finite feasibility evaluation iff quantified grid-placement feasibility, including an allowed-but-too-far boundary witness.
3. First sufficient stage carries all prior insufficiency certificates; no premature avoidance relaxation or start-side truncation.
4. Selected ordinary output belongs to the relation; emergency output requires its separate guard and positive cursor progress. A theorem returning an unresolved provider result is labeled accordingly.
5. Finite execution decreases a well-founded measure and preserves source order/content coverage under admitted continuation contexts. History admission is separate from one-decision soundness.
6. Independent scenarios S1–S8 are either inhabited and discharged or explicitly outside the approved domain with the reason retained. No simulated browser outcomes.

Semantic mutants should remove the Rule 2 all-auto guard, conflate page/column avoidance, weaken one line-count comparison, relax avoidance before lines, truncate start with end unconditionally, replace insufficiency with no allowed candidates, or allow an emergency zero-progress step. Require actual semantic disagreement or proof failure, not syntax failures. Keep a source-to-definition ledger for every supported clause and every retained dependency.

## Approval decisions needed

Approve or revise the restricted geometry/sufficiency interpretation; settle continuation line-count inputs; choose the emergency opportunity region; accept the explicit B/C reading while retaining the source ambiguity; decide whether ancestor type-specific values belong in the initial domain or an explicitly queued extension. These are semantic choices, not reasons to build a large generic framework. The source importer and all whole-CSS obligations remain unchanged regardless of the pilot boundary.
