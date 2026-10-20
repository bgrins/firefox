# Proposed delimiter-continuation component

Dependency: frozen `css-parser-nested-control-v3`, root scoped acceptance retained under predecessor/. Use `NestedControl.untilBefore`, `RawRecovery.recover_complete`, `RawSafety.recover_pending_none`, and the existing source-only stack/annotation semantics.

## Independent relation

Describe completion by ownership, not by repeating the native if-statements:

- Callback Stop/error: retain the callback/exhaustion state and result exactly, after restoring the enclosing stop mask; do not advance, clean pending blocks or emit new observations.
- Physical EOF: same result/state after the completed prefix recovery.
- Enclosing-owned boundary: leave that delimiter unread, including overlap between enclosing and requested masks.
- Requested-only noncurly punctuation: consume exactly that punctuation in the source-only token relation, with no function-observation or annotation event; native cursor advances one ASCII byte and cache remains unchanged.
- Requested-only opening curly: consume the entire component block with an explicit initial curly stack, including its matching close if present or EOF otherwise. Append precisely its raw observation/annotation effects; leave subsequent source available.

Prove result preservation, cursor/reference alignment, restored stop/depth fields under represented callbacks, pending-none on completed recovery branches, coherent unchanged cache, and exact annotation/observer equations. Do not assert unchanged annotations for the curly branch or unchanged caller-selected limit for arbitrary callbacks.

## Required premises to discharge or retain explicitly

1. Native mask realization: requested bytes are from `{`, `;`, `!`, `,`; enclosing stops may also be the three closing delimiters. A mathematical arbitrary byte list is not automatically a native mask. Duplicate lists denote sets; snapshot encodings must be canonical if equality is claimed.
2. Valid cursor/token boundary and immutable UTF-8 source; lexical byte progress and bounded end positions. `recover_complete` supplies EOF-or-union-boundary under the existing progress premise.
3. Delimiter lexical provider law: requested-only punctuation has width1; no newline, annotation or substitution observation; `{` initializes the independently described curly component. This cannot be replaced by a premise that the resulting complete state is correct.
4. The accepted source-only cleanup stack semantics, including pending-none and annotation writes. Existing finite native agreement does not prove the whole tokenizer implementation.
5. Callback grammar and same-parser saved-state contract. Do not generalize to arbitrary host mutation, invalid saved positions, panic/unwind or allocation failure.

## Distinguishing cases for later native/model agreement

- Same delimiter in both masks: inner after must leave it to outer before.
- Only outer closer appears: never consume it, even after callback failure in Consume mode.
- Requested semicolon followed by valid declaration: consume one byte, retain suffix.
- Requested curly containing semicolon, nested function and mismatched square closer: stop only at matching curly; preserve following rule.
- Unterminated curly: EOF completion, no invented close byte.
- Callback leaves a pending function then errors: Stop preserves pending state; Consume clears it and reaches the boundary.
- Cached semicolon/curly created by a saved-state read/reset: direct advance must not install a fresh cache entry; future reset/re-read remains coherent.
- Curly with sourceURL A and nested sourceURL B: source-only raw writes determine final annotation. Punctuation outside the body adds no write.
- Function observation enabled before recovery: raw skipped var()/env()/attr() are observed according to the existing mode contract, while delimiter advancement adds none.
- Synthetic provider without byte progress, or arbitrary non-ASCII stop byte: must remain outside the native correspondence, not vacuously count as completion.

Meaningful mutation targets: consume outer-owned delimiter; omit direct advance; omit curly cleanup; consume despite Stop/error; clear/update cache on raw advance; erase curly annotation writes. No new broad finite corpus is needed before these concrete distinctions are modeled.
