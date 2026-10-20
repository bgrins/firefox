# Nested control milestone: source scope before model

## Retained native source

SOURCE-PINS.json retains complete exact local parser.rs/tokenizer.rs, LinkParameters::parse, VariableValue::parse and declaration scanner, and DashedIdent::parse. The parser/tokenizer are byte-identical to the accepted wrapper-history source. LinkParameters is unchanged; VariableValue includes the separately owned current whitespace/metadata repairs and is not asserted to match older compiled binaries.

The next model must compute token reads, pending-block cleanup and byte-delimiter recovery. It will not take a correct observer trace or an abstract enter/exit event as an input.

## State and transitions

Extend PublicCache.State with current stop set, current_block_depth and nested_block_limit. Depth/limit use8-bit wrapping arithmetic, including limit0 meaning unlimited. Existing State supplies cursor/pending, cache, tracking mode, annotations and saved cursor snapshots. Native line location, error payloads, allocations and panic unwinding remain outside the initial projection.

parse_nested_block takes and clears the pending opener first. Missing opener is a panic precondition, not a normal parse error. If limit is nonzero and current depth is at least limit, it consumes the requested block directly, does not invoke the callback, and returns the depth-limit error. Otherwise it increments depth, replaces (does not union) the stop set with the matching closing delimiter, invokes parse_entirely, skips any pending block left by that callback/probe, consumes through the originally opened block's close or EOF, restores the old stop set and decrements depth. Cleanup runs after both successful and failed callback results. Reset inside a failed try_parse restores ParserState; it does not roll back cache, tracking or annotations.

Raw recovery is source-shaped. consume_until_end_of_block maintains a stack of opening block types; each next_unchecked read updates observer and comment directives and leaves cache untouched. A matching close pops the stack; mismatched closes are consumed without popping. Raw progress/byte bounds are lexical-provider obligations; finite fuel is justified under that progress contract, not assumed to represent physical EOF.

parse_until_before temporarily unions the existing stop set with the requested delimiters, invokes parse_entirely, and restores the old stop set. Stop-on-error returns immediately. Otherwise it first skips pending block content and then loops: inspect the next raw byte, stop before a union delimiter, else next_unchecked and skip any resulting pending block. The result remains the callback/exhaustion result even if recovery sees more tokens or attributes.

parse_until_after uses that result, then consumes a found delimiter only if the restored outer stop set does not own it. It advances one ASCII byte directly; consuming an opening curly delimiter additionally consumes its complete block. This direct byte step does not imply a token/cache observation. Keep that distinction explicit.

## Composition plan

1. Define raw recovery native and source-only reference functions using existing PublicCleanup/PublicSourceOnly token-stack machinery and literal byte checks. Prove cursor, cache, observer and annotation effects from reads. This should reuse existing cleanup lemmas where exact, rather than admit a trace.
2. Define normal-return nested/until control state transitions around represented callbacks; prove restoration of outer stop/depth and relevant-observation refinement. The accepted WrapperControl program supplies entirely/attempt behavior for already represented bodies. If callbacks contain nested wrappers, recursively translate those bodies rather than label them as atomic correct events.
3. Carry callback grammar predicates separately from the coarse Token observation projection. For an initial real callback translation, use LinkParameters empty-value lists with source-calibrated expect_function_matching, DashedIdent, expect_comma and empty VariableValue paths. Preserve the distinction between observer completeness and property grammar acceptance.

## Concrete real callback paths

Success: `param(--x,),param(--y,)`. The initial try_parse(expect_ident_matching none) observes a Function then rewinds. The comma-list loop skips whitespace and establishes a comma bound. Each callback consumes param(), enters nested parsing, consumes a dashed ident and comma, then VariableValue::parse peeks the closing delimiter and scans an empty declaration value under Bang/Semicolon bounds. Nested and outer entirely checks succeed, each closing parenthesis is consumed by cleanup, and the list loop consumes its comma. Only the final successful return publishes the ArcSlice of two entries.

Failure with useful recovery: `param(--x,),bad(var(--y))`. First item succeeds. The second callback consumes bad() and fails expect_function_matching param before nested entry. parse_until_before's Consume behavior must then skip the pending bad block, observe var(--y) through raw tokenization, and leave the comma-list function returning Err without publishing the partial list. This directly tests a real caller whose error path has additional observations.

Further case: `param(--x,),param(--y var(--z))` fails expect_comma inside nested parsing. Cleanup must retain observation/cache/annotation effects while restoring outer stop/depth. It can follow after the first two paths if required to distinguish nested versus delimiter recovery.

## Admissions and limits

Actual tokenization of nonselected lexical families, UTF-8 validity, progress, precise source-to-token payload grammar, declaration-value serialization and allocations are distinct providers. The initial empty-value translation avoids claiming to verify the complete recursive VariableValue grammar. LinkParameters stores text only and has the separately audited taint-provider gap; this parser-control milestone neither fixes nor proves its security provenance.

No browser/native-production/build/Git edits. Own compiler outputs may be generated for this artifact and removed after terminal evidence capture. Parent owns deciding when these source/model obligations are sufficiently composed to claim a milestone.
