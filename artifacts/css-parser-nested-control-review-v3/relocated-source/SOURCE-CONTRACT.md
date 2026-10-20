# Source contract

Exact retained bodies and hashes are in SOURCE-PINS.json. Discovery logs are in searchfox/. The local parser and tokenizer match the previously reviewed wrapper-history source. The retained VariableValue source includes the separately owned current repairs; these claims do not bind an older browser binary.

| Native operation | Model | Contract and omitted fields |
| --- | --- | --- |
| ParserState::take_at_start_of | NestedControl.native / LinkEmpty.nested | Takes and clears the pending opener. Missing opener is a native panic, represented only by an outside-contract sentinel. |
| parse_nested_block | NestedControl.native | 8-bit depth and limit; nonzero limit rejects after raw consumption; otherwise replace stop set, increment, parse_entirely, skip pending, consume original block, restore stop/depth. The represented body is a WrapperControl.Program. Normal return only. |
| consume_until_end_of_block | PublicCleanup.run / PublicSourceOnly.cleanup | Imported source-shaped stack loop, matching versus mismatched closers, raw reads, observer/annotation effects. Fuel equals remaining bytes. Progress is a named provider premise, not a consequence of observer alignment. |
| parse_until_before | NestedControl.untilBefore / RawRecovery.recover | Union outer and requested delimiter sets, entirely, restore outer set, Stop-error early return, initial pending cleanup, raw-byte delimiter checks, next_unchecked and pending cleanup. |
| next_unchecked | PublicCache.fresh read false | Cache untouched; tokenization changes cursor, observer and annotations. RawSafety proves the pending-none precondition is maintained. Cursor line/column bookkeeping is omitted. |
| parse_entirely / expect_exhausted | accepted WrapperControl | Exhaustion is bounded by stops; failed lookahead restores cursor but retains cache/mode/annotation effects. |
| LinkParameters::parse | LinkEmpty.parse / commaLoop / item | Initial try(none), comma-list skip and bound, expect param(), nested callback, then success/failure. Empty-value restriction only. The finite loop fuel is sufficient for the six checked paths; universal caller termination is open. |
| DashedIdent::parse | LinkEmpty.expectIdent | expect_ident plus starts_with("--"). Identifier payload comes from the retained Name/URLDispatch projection at the fetched cache key. This grammar bridge is source-reviewed and concretely calibrated; no universal payload-to-native callback theorem is claimed. |
| VariableValue::parse / parse_declaration_value | LinkEmpty.emptyValue | Leading whitespace peek/reset, Bang/Semicolon bound and empty scanner EOF. The full recursive scanner, serialization, allocation and nonempty values are outside this translation. |
| parse_until_after | None | Still open: direct ASCII delimiter advance, outer-stop ownership and curly recovery must be modeled separately. |

## Theorem boundaries

RawRecovery and NestedControl refine independently computed source-only token histories; no correct observer trace is supplied as a premise. Observer alignment requires coherent cache and compatible enabled names, as in the accepted dependencies. Raw recovery additionally proves cache retention, exact comment-directive writes, cursor progress and byte-fuel completion under PublicCleanup.Progress. RawSafety proves pending-none invariants and the complete recovery annotation relation.

Native stop lists must contain only native delimiter bytes, and denote sets. Arbitrary List Byte stop values in the mathematical definitions have no automatic native realization. Depth/limit are Fin 256. Represented program callbacks do not call the public set_nested_block_limit API; a callback that does so can persist a changed limit and is outside that program grammar. The limit/depth fixture setters are whitebox boundary controls, not claims that every injected state is reachable through ordinary parsing. Native exceptions, panic unwinding, allocation failure and line locations are omitted.

LinkComposition proves the higher-order wrappers used by the concrete caller agree with the already proved program wrappers when given a program body. It does not prove arbitrary higher-order callbacks preserve controls. LinkPaths proves six concrete byte-input outcomes with kernel reduction (`decide +kernel`), under its explicit lexical provider. The native calibration exercises a fail-closed provider on the same paths; unsupported families are not silently accepted in the driver. No theorem states full Stylo callback equivalence for all CSS text.

LinkParameters stores OwnedStr and has the independently recorded provenance gap. Neither taint propagation nor URL-sink confidentiality is established here.

## Concrete caller outcomes

- `param(--x,),param(--y,)`: success; no substitution seen; cursor at physical EOF; no pending block; restored stop/depth.
- `param(--x,),bad(var(--y))`: expect_function_matching fails on bad(); comma-bound recovery discovers var(); failure returns without publishing the partial list.
- `param(--x,),param(--y var(--z))`: failed expect_comma reads var(); subsequent nested cleanup preserves that observation; failure prevents list publication.
- `none` and `param(--x,)`: success without substitution.
- `param(--x,),`: fails the next required item.

The model records success and parser state, not ArcSlice allocation or the returned values. The no-partial-publication claim follows from the retained Rust `?` before constructing the final ArcSlice, not from a modeled heap.
