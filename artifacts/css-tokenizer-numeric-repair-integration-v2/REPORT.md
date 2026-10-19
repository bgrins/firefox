# Exact numeric v2 integration

## Bound source

The candidate tokenizer has SHA-256 `5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211`. The original is the sealed lexical baseline `8a5925e228e5838ef6afcaf165b27037cf48d0daa31f0bef3d42338c30ff51ab`. Root identifies the accepted repair as stack commit `4391deb4751a8be2be98e838360f00c94808c5d5` and independently landable commit `12c1208d2c4f485942164b7df7c276401b8e7b8c`; this artifact does not mutate or independently inspect Git.

The checker removes exactly the new start-position capture and fallback block from the complete candidate file and requires byte equality with the original. The start capture precedes numeric sign consumption; the fallback precedes integer publication, percent and name consumption. It binds all eleven complete relevant tokenizer methods, the checksum, and the retained Rust standard-library source/documentation. The fallback guard is length >=256 or nonfinite; neither the loops nor lexical output branches change.

## Kernel results

- `FromStrGrammar` gives independent inductive signed-decimal and exponent productions, then the documented Rust numeric productions (integer, digits-dot-optional-digits, optional-digits-dot-digits, optional signed exponent). Literal digit membership is checked for every byte. Actual native-entry admission derives the consumed numeric prefix's grammar membership; no caller-supplied token list or numeric-validity assumption substitutes for this derivation. Uppercase E is admitted because Rust documents the grammar after lowercasing. Infinity/nan spellings are unnecessary for this numeric consumer. “Finite number” in the model means decimal spelling, not a promise of a finite floating result.
- `NumericCapture` proves the slice from the saved start to the numeric end equals the consumed ASCII prefix. Forward positions justify subtraction; end/start lie within the complete source and any admitted native maximum. Under the inherited encoded-unit relation, both saved start and numeric end are return boundaries. The model retains nonzero prefix positions.
- `NumericRepair` composes grammar membership with an explicit standard-parser acceptance contract. This excludes a parse-error unwrap for the model under that contract. Any successful result has the same complete lexical projection as the original: kind, count, suffix, decoded unit, sign and syntactic integer/type, plus the inherited selected dependency summary. The payload is allowed to change. A rejecting-library witness remains, so normal completion is not asserted without a library contract. A separate witness changes payload while preserving the projection.

The three new modules extend the original model; they do not redefine or weaken its lexical obligations.

## Source and native bridge

The actual whole original and candidate cssparser sources are rebuilt with the retained direct-source dependency closure. Ninety retained cases compare lexical observations and whole-scanner control flags while recording f32 payload bits separately. Three known compensated-exponent rows change from infinity/NaN to 0.5; those observations are not a universal numeric theorem.

A separate candidate build adds one removable logging statement immediately before the fallback. It records saved start, current end and actual borrowed slice. Eighty-one retained numeric cases plus three nonzero UTF-8-prefix cases match an independent ASCII grammar regex and exact byte offsets. The trace instrumentation performs allocation/logging and is not presented as a bit-identical production executable; the uninstrumented pair is also rebuilt. The complete inserted statement is retained in output.

A native semantic mutation extends the borrowed numeric slice by one byte into a following unit. It compiles, then Rust FromStr rejects the now-incomplete exponent and unwrap panics. The matched model slice observation also differs. This distinguishes correct prefix capture from merely having an individually valid input somewhere in the source.

## Remaining trust and scope

The Rust FromStr implementation, parsing termination/normal completion, float classification, allocator, compiler and core/string contracts remain trusted. The retained library source documents acceptance of the proved grammar; dec2flt and its numeric correctness are not kernel verified or rebuilt independently of the toolchain. No exact f64/f32 value, rounding or actual i32-value preservation is inferred. The original arithmetic counterexamples remain sealed in the predecessor; the repair's separate numerical bounds and browser acceptance are not replaced by this lexical transfer.

The model treats parse as a pure borrowed-input operation. Actual code supplies only an immutable string slice and assigns the returned value, preserving parser state; this is a source/API admission, not a full Rust aliasing/compiler proof. Projection preservation is conditional on successful normal completion. Allocation failure, library panics outside parse rejection, or native metadata overflow are not ruled out universally.

Mathematical source positions correspond to usize only under admitted representation bounds and ordinary defined arithmetic. Derived start/end bounds justify the new subtraction and slice within that relation; they do not verify every Rust operation in the complete tokenizer. Initial entry/source identity, valid UTF-8 and the codec relation are inherited. Parser position debug assertions require these boundary facts. Name/escape decoding still requires packed u32 metadata headroom (`advance_line_number` adds `count << 2`), as well as usize and allocation normal completion. Ownership state remains a native projection, not independently specified universal ownership semantics.

The native harness retains the handwritten var/env/attr `SubstitutionFunctionKind::from_ident` shim. The actual helper body is compiled; the derive expansion is not. Numeric direct observations do not depend on the shim, while whole-scanner control columns do. `inputs/shim/SCANNER-PROVIDER.md` preserves that qualification.

Fast dispatch is disabled in the direct Rust replay, with the separate signed dispatch correspondence inherited. Full general tokenizer restart, all other token consumers, block parsing, declaration/graph algorithms and native heap/metadata closure remain open. This component is an exact additive lexical integration, not a claim that full CSS or tokenizer verification is complete.

## V2 packaging correction

The first source-frozen integration replay passed. Root requested a non-pictographic supplementary letter in the new nonzero-offset fixture, an exact theorem-name inventory, and a tamper gate. V2 uses U+10000 after U+00E9 in that prefix, checks all 158 theorem names in module order, and rejects a modified source before creating its requested output directory. The 23 proof modules and their theorem statements are unchanged from v1. Historical signed input capsules remain byte-identical, including their older retained corpus. No theorem or library admission was reduced.
