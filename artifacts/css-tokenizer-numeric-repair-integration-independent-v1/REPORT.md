# Independent review: numeric repair lexical integration v2

## Decision

Accept the sealed component's **conditional lexical transfer**. No source/model blocker found within its stated scope. Fresh relocated source replay passed. This does not accept a universal numeric-value theorem, whole tokenizer correctness, native memory safety, or Rust standard-library implementation correctness.

The reviewed producer FREEZE is `fb3e9cc30c276a3cce92324666aa078fbaefb4656e21ca942ffd6396013c88f1`, MANIFEST `8c804f1ea9d82b91b186f2dacd94a5a08b153d5e3e10c8ffffaaceccb8422d2b`. All 454 inputs were independently hashed before reading/importing executable helpers, then copied into `input/`. Parent lexical, repair and shim capsules retain their original hashes. The live tokenizer was read-only checked during review and matched candidate `5319a01e403cd2a93bfc3dd4c53a7e5ec95129360da58c6f9f76f480ae5e6211`; this is a point-in-time identity check, not a future-live-tree requirement.

## Substance of the three new modules

### FromStrGrammar: ten audited results

The independent grammar uses literal ASCII digit membership and inductive sign, mantissa and exponent productions. It does not define valid input as whatever the native scanner consumed. Its mantissa requires at least one digit and, if the decimal point is consumed, a nonempty fraction. The proof derives the necessary nonempty integral/fraction alternative from actual numeric-entry admission. Exponent acceptance requires E/e, optional sign and at least one digit; incomplete exponent text remains outside the captured prefix.

The separate Rust grammar admits integer, trailing-dot and leading-dot forms. The proved numeric grammar is a subset: a trailing dot is not consumed by this CSS numeric consumer, so that extra Rust production is harmless. The outer sign, exponent sign, uppercase E, leading zeroes and no-whitespace requirement agree with the pinned Rust documentation. Infinity/NaN literals are not needed for this consumer's lexical domain; long decimal spellings that evaluate to infinity remain admitted. `FiniteFloat` names a decimal spelling, not finite arithmetic output.

The literal digit-domain check plus structural proofs are substantive. Sign/exponent primitives still originate in the inherited lexical model; this component does not independently derive all native tokenizer byte operations from Rust semantics.

### NumericCapture: nine audited results

The full source is split into arbitrary preceding bytes and the current input. The saved start is the preceding length; end is start plus the already-proved consumed lexical prefix length. The proof derives forward movement, bounded end, subtraction, exact slice equality, ASCII membership and grammar membership. These are universal finite-list statements, not just observations at offset zero. Three native fixtures additionally exercise a nonzero prefix containing U+00E9 and supplementary U+10000.

The boundary results inherit the encoded-unit relation and marker predicate. They are not an independent proof that arbitrary lists form valid UTF-8. A valid native Rust str, correct source/position correspondence and defined usize arithmetic remain required. Native length bounds justify the newly added subtraction and borrowed slice within that correspondence; they do not prove every earlier lookahead addition or metadata counter cannot overflow.

### NumericRepair: nine audited results

The model's fallback matches the length/nonfinite guard, reparses exactly the captured bytes, and allows the payload to change. `LibraryAccepts` is an explicit universal grammar-acceptance assumption. From the proved input grammar it derives a successful modeled parse result. The rejecting-library witness demonstrates that normal completion is not unconditional; the changed-payload witness demonstrates that the projection theorem is not secretly preserving numeric values.

Projection is intentionally a small wrapper theorem: candidate construction pairs the unchanged lexical token with a new payload. Its source meaning depends on the exact native delta and the standard parser's immutable borrowed-input API being pure with respect to the tokenizer. It is not an independently mechanized Rust execution proof. Once admitted, equality of NumericToken.Result preserves kind, numeric syntax/sign/type, decoded unit, count and suffix, and the inherited deterministic tokenFlags projection. No new explicit whole-scanner theorem or i32-value equality is obtained from that equality. The original integer-selection expressions remain conditional symbolic arithmetic facts.

## Exact native/API bridge

Read complete consume_numeric and all eleven bound helper definitions. The checker deletes exactly the saved-position statement and the fallback block from the complete candidate and obtains the original `8a5925e228e5838ef6afcaf165b27037cf48d0daa31f0bef3d42338c30ff51ab` byte-for-byte. Capture occurs before sign consumption. Fallback occurs after the numeric loops and before integer publication, percentage handling or dimension-name consumption. There is no parser mutation in the added assignment: slice_from borrows through an immutable receiver and parse returns a value assigned to the local f64. Core string/slice and compiler semantics remain trust boundaries.

The pinned Rust 1.92.0 source documents the admitted decimal grammar and delegates FromStr to dec2flt. The component neither verifies nor independently rebuilds dec2flt and its submodules. Library termination, allocation/panic behavior beyond modeled parse rejection, IEEE classification, rounding and actual f64/f32/i32 values remain outside the proof. The API contract gives a strong practical justification for unwrap on this grammar, but is still an assumption in the kernel theorem.

The native pair rebuilds the actual full cssparser original/candidate from retained source with fast dispatch disabled. Its comparison omits only the payload-bits column, retaining the lexical and scanner observations. Handwritten var/env/attr from_ident remains in the enclosing scanner facade; direct numeric rows do not rely on it, scanner-control flags do. The original codec, owned/borrowed representation, metadata headroom, allocator/compiler and dispatch admissions are preserved, not discharged by this transfer.

## Fresh verification

Own relocated `input/check.py` replay exited 0. Exact inventory: 23 modules and 158 standard-axiom reports, of which 130 are inherited and 28 new (10 grammar, 9 capture, 9 wrapper). No sorry/admit/axiom/native_decide accepted. The checker rejects a changed Lean source before creating the requested output directory.

The uninstrumented source pair passed all 90 retained rows; three compensated-exponent payloads changed as intended and were retained separately. The instrumented candidate supplied 84 captures, including three nonzero UTF-8 starts, matching an independent ASCII-prefix regex and exact byte offsets. Its one logging insertion is explicit and is not claimed to preserve allocation/performance behavior. The compiled slice-extension mutant consumed a following unit byte and exited 101 on ParseFloatError; the corresponding Lean slice comparison was false. No new finite matrix or benchmark was added. Original mutation families remain retained predecessor evidence and were not rerun by this integration replay.

Receipts under `evidence/` contain this review's actual commands/results, not producer success copied as own execution. Compiler outputs are excluded from the sealed source inventory and can be regenerated using check.py --replay.

## Remaining obligations

- Native-to-model state/byte correspondence, valid UTF-8/codec, machine integer and metadata bounds, normal allocation and compiled library behavior.
- Any universal exact numeric-value or i32-value claim; separate v2 bounds/source review remains distinct.
- Derived substitution-kind parsing and a complete scanner/declaration caller refinement.
- Whole tokenizer restart and all other token consumer semantics.

No browser, live source, Git/index or Mach mutation was performed for this review. No new CSS conformance finding is manufactured from this component.
