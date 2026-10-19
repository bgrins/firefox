# Resolved unit summaries: independent native and WPT review

## Provisional source verdict

No blocker found in the reviewed candidate. The native delta implements the earlier scanner design exactly and the fixed 21-case WPT has a defensible oracle. Final authentication and retained standalone receipts will be recorded separately when the producer seals the package. This report does not approve an unrun Firefox binary or claim full CSS verification.

This is an independent review of the implementation and tests. I previously proposed/reviewed the one-token suffix scanner architecture; that design contribution is explicit. The native implementation and WPT were produced by another agent. No live native/WPT files, Git state, browser, or Firefox build were changed here. The inline WPT script passed `node --check`; no browser was run by this reviewer.

## Exact native changes

`native.patch` adds `resolved_token_dependencies`, adds private `VariableValue::new_resolved`, and changes precisely these two calls:

- The attribute arm of `substitute_references_if_needed_and_apply`.
- The universal-registration arm of `Substitution::into_value`.

The shared `VariableValue::new`, typed computation branch, existing serializer, substitution selection, graph traversal and original parse-time flag collection remain byte-identical. The new constructor delegates to the old constructor, then updates only `references.flags` on `Some`. CSS bytes, URL data, first/last token kinds, `explicitly_attr_tainted`, empty references vector and caller `attr_tainted` assignments retain their prior behavior.

An important downstream check: `References::has_references` tests the references vector, not flags. Adding a non-custom unit summary therefore does not falsely make the persisted value require another substitution pass. The universal no-reference fast path continues to clone the value with its summary. The attribute-taint predicate checks ATTR/explicit taint, neither of which the scanner adds.

## Scanner semantics and risks

The helper constructs a new Parser on the current suffix, consumes exactly one token including whitespace/comments, and advances by the returned byte position. It cannot invoke the previous-token block skipper on an opener because the parser is discarded before a second token call. No recursive walk or artificial depth cutoff is introduced.

Only decoded Dimension units are passed to the existing `ReferenceFlags::from_unit`. This preserves all current font-relative classes, including lh's font+line flags and rlh's root-font+root-line flags. Function names use the existing `SubstitutionFunctionKind::from_ident` classifier. Strings, comments, unquoted URLs, identifiers, numbers, grouping/closing tokens and other inert tokens do not add flags. Quoted URL contents are string tokens and remain inert. Escapes and numeric exponent syntax remain cssparser's responsibility.

The first tokenizer call on nonempty input consumes a complete token and advances to a UTF-8 boundary. `debug_assert!(consumed > 0)` checks this invariant in debug configurations; release termination still relies on that tokenizer contract. Parser initialization is fixed-cost. There is no input-dependent call-stack nesting. Escaped token decoding can allocate, and this review does not prove allocator success or machine safety.

The helper is not a syntax validator: grouping tokens are flattened and mismatched/unclosed closers are not diagnosed. Its exact-summary contract assumes admitted valid values. It rejects BadString/BadUrl tokens, but that does not turn it into a full validity check.

On a remaining recognized var/env/attr function, or bad string/URL, it returns `None` immediately and the constructor retains its old empty references. Already accumulated flags are discarded, so no partial summary is installed. Env link payloads can reach this branch because their returned CSS is not recursively substituted. This is deliberately preserved incomplete behavior, not proof of exact zero dependencies. The selected-output Lean component is applicable only with its corresponding completeness/source-admission premises.

Scanning each materialized value adds linear work over its bytes. This is a necessary cost of this narrow repair's chosen summary reconstruction; no performance measurement was performed. The patch has no global cache, shared mutable state, or new provider interaction.

## WPT oracle and discrimination

Fixed test SHA-256: `7fac42de6c2b882d669f0806f613f0e1e454cdd2090723ad1d12237c9e6531f9`.

The registered length has a computationally independent 11px initial value and does not inherit. Each ordinary fixture supplies a parent with 23px font and 37px line-height; the root is explicitly 19px/29px. Pixel values avoid font-metric and platform assumptions. Width consumption additionally checks the value reaches an ordinary property. Cleanup removes every fixture.

| Cases | Independent expectation / distinction |
| --- | --- |
| Attribute and universal em cycles | The registered length depends on current font-size, and font-size references that registered value. Cycle handling gives registered initial 11px and inherited font-size 23px. |
| Attribute font ordering | Explicit 17px target font must be established before computing the surviving 1em registered length. Parent 23px is a discriminating wrong result. |
| Absolute attr and literal registered controls | 13px is acyclic and gives 13px throughout; a direct 1em registered cycle establishes existing cycle behavior independently of either new sink. |
| Escaped units | Attribute `1e\\6d` and universal `1\\65 m` decode to em. They have the same cycle as ordinary 1em. The universal row reaches the scanner with escaped tokens; typed attr serialization may normalize its unit first. |
| Nested calculations | The selected expression retains an em dimension, so it has the same font cycle. This checks traversal below ordinary functions. |
| lh ordering | Target line-height 31px differs from parent 37px and target font 17px. A selected 1lh length must become 31px. |
| rem/rlh on non-root target | The reference is to explicit root 19px font / 29px line-height, not local or parent metrics. Expected values are 19px or 29px with no local font cycle. These are not root-element self-cycle tests. |
| Comment and separator controls | Comment text is inert; calc(13px) is acyclic. Separate number and ident in `1/**/em` do not become a length: typed registration falls back to 11px, which font-size can validly consume as 11px. |
| Inherited substituted universal | Unregistered --raw inherits its substituted 1em token value, not a parent-computed 23px length. Its typed consumer on the child uses the child's 17px font. |
| String controls | Attribute strings remain strings, including apparent var/lh text inside quotes. Invalid font-size inherits 23px without corrupting the registered string. |
| URL controls | Universal URL values resolve relative to the document URL; the typed registered URL retains that value. Font-size rejects the URL and inherits 23px. No resource load is required. These rows avoid attr URL-taint restrictions. |

The typed attribute comment/escape cases can be normalized before the scanner runs; their WPT pass alone would not establish lexical comment/escape handling. The universal escape row and exact standalone scanner inputs address that distinction. Conversely, standalone scanner results do not establish graph timing or inheritance, which is why the browser cases matter.

Primary/fallback selection and root-element self-cycle behavior are not comprehensively covered by these 21 cases. Existing graph/fallback regression suites and the scoped Lean component remain separate evidence; this review does not request a larger corpus without a concrete remaining defect. The new source does not change branch selection or root normalization.

Normative basis: registered-property cycles add font/line-height dependencies for relative units; universal/unregistered computed values retain substituted token values rather than performing typed length computation. Attribute type substitution parses the selected attribute value. [Properties and Values API](https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles), [CSS Variables](https://drafts.csswg.org/css-variables-2/#defining-variables), [CSS Values](https://drafts.csswg.org/css-values-5/#attr-substitution). Current primary snapshots were already read and retained in the preceding scanner/model reviews; no new spec interpretation is needed for these fixed cases.

## Standalone harness admission

The inspected harness extracts the exact helper, unit classifier, flag definitions and all 12 unit string constants. It supplies a small from_ident adapter based on the enum names and retained derive template rather than compiling all style_derive. That must remain an explicit boundary. Its cssparser configuration omits the default fast-match optimization used by the Gecko build. A full build is still required.

The final reported scanner case count is 49, with individual unit rows added so grouped OR results cannot hide a missing classifier arm. The separate depth stress uses 100,000 groups of three nested blocks, i.e. depth 300,000, on a requested 64KiB thread stack. These are bounded implementation checks, not universal native refinement. This reviewer has not executed that Rust harness; final authenticated producer receipts will be identified in the addendum.

## Remaining acceptance gates

- Authenticate final original/candidate/WPT bytes and standalone source-only receipt against the producer seal.
- Root's build and paired browser suite must establish the actual native candidate behavior, with stable source/resource/binary pins.
- Preserve incomplete-env compatibility and the conditional proof boundary in the final handoff.

No source or WPT oracle correction is currently requested.
