# Pre-proof unordered-combinator contract review

No blocker to implementing the proposed restricted operator contract. This review precedes implementation; it approves the semantic target and frozen oracle, not proofs or a new recognizer. Root retains implementation authorization.

## Specification and grouping

The pinned source and current rendered CSS Values4 agree that grouping matters and that a flat unordered group differs from an explicitly nested group. The proposed n-ary indexed-occurrence model with contiguous complete child matches respects that distinction. Operator precedence is also correct. The specification explicitly includes a nullable-operand zero-or-more pattern, so refusing nullable children must remain a supported-domain restriction, not CSS invalidity. [CSS Values combinators](https://drafts.csswg.org/css-values-4/#component-combinators), [patterns](https://drafts.csswg.org/css-values-4/#combinator-multiplier-patterns).

Do not turn a flat chain into binary nesting, or flatten brackets during parsing. A required nonnullable child may contain optional parts. For example, a? b is nonnullable as a complete child, whereas [a b]? is nullable. Validate every unordered node recursively: a nullable operand in a nested unordered node cannot be hidden by appending a required token outside it. This is an implementation obligation consistent with the written contract, not an expansion of supported nullable semantics.

Equal child grammars must retain separate indexed identities. Include a || a admitting both one and two a tokens, while rejecting three. This checks occurrence identity rather than set-of-keywords deduplication. Repeated selection of the same index remains forbidden. Nested grouping needs both an acceptance and an interleaving rejection control.

## Frozen baseline and oracle

The historical extractor bytes match BASELINE.json and independently still refuse the recorded grammar with Unsupported double-bar combinator. The oracle hash matches its pre-implementation receipt. An independent category/cardinality predicate checked all 1,555 sequences of length zero through four over the six relevant keywords; its accepted set equals the 38 distinct frozen rows. Counts are six singletons including none, fourteen pairs and eighteen triples. Maximum accepted length is three, so the bounded check also includes the first impossible length.

The reviewed text-transform grouping treats none as the outer alternative and the three case keywords as one component choice. This follows the property grammar and combinator precedence; it does not formalize text transformation behavior. [CSS Text3 property](https://drafts.csswg.org/css-text-3/#text-transform-property).

The oracle is independent of the future enumerator and parser implementation. It covers this property exactly, but cannot substitute for generic grouping, duplicate-occurrence, nullable or remainder proofs. Preserve the oracle and historical refusal unchanged while adding the opt-in path.

## Required independent semantic interface

Lowering into the existing Grammar is a useful implementation strategy, but lowering alone does not supply independent semantics. Define matching directly using a nonempty ordered list of pairwise-distinct bounded component indices, each selected child matching one complete contiguous chunk, with those chunks concatenated in the selected order. That relation must not mean membership in the implementation's enumerated alternatives or matching its lowered grammar.

Then prove ordered-subset enumeration sound and complete for that index relation, connect each selected sequence to the existing Grammar Matches relation, and prove exact input/remainder correspondence for the lowering. Acceptance on empty remainder is a corollary; an acceptance-only theorem would miss prefix/remainder bugs. The existing keyword/alt/seq/optional matching laws are reusable proof components, not proof that CSS prose was mechanically derived.

Prove the nullability predicate corresponds to an empty complete match, including alternatives, sequences and optionals. Guard arity at least two, sufficient stack operands and recursive supported-domain validity. Preserve stack operand ordering while recovering the n-ary node. Old-op embedding must preserve decoding and matching; a few old fixture examples alone are weaker than that compatibility claim.

An enumerator may produce duplicate grammar alternatives when distinct occurrences have equal text. That does not affect language equivalence, but must not be confused with permission to collapse occurrence identities before selection. State whether the result theorem is language/remainder membership rather than output-list multiplicity or ordering. Structural recursion with finite inputs avoids arbitrary fuel; factorial growth remains an implementation cost, not a reason to silently truncate accepted semantics.

The author confirmed the independent Fin-index/Nodup relation, recursive rejection, duplicate-occurrence and exact-remainder controls before implementation. Unsupported &&, typed productions, other absent contexts, raw tokenization/escaping/case folding, CSS-wide values and rendering semantics remain explicit refusals or exclusions. No Stylo/native implementation or canonical library change was performed by this review.
