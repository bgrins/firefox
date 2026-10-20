# Delimiter-provider bridge: independent review

## Verdict

The five root theorems are sound at their stated model tier. The bridge replaces an opaque delimiter contract with a precise three-byte provider-width premise. The exact finite-driver provider satisfies that premise for arbitrary suffixes. It does **not** satisfy the separate globally quantified provider-progress premise; consequently this review does not instantiate the full `after_refines` theorem for that driver.

`lean/ProviderReview.lean` contributes 12 kernel-checked results. `ReviewAudit.lean` audits those and all five root results. Fresh compilation receipts and exact axiom inventory are retained. The root module is copied without changes, and both complete retained Rust files matched the current local files at review time (SOURCE-COMPARISON.json).

## Substantive proof review

- `selected_false` proves none of the four requested bytes begins the identifier branch, independently of suffix. It does not merely assume the desired delimiter token.
- `relative_delimiter` unfolds actual ByteLex dispatch. Curly opening is handled directly; semicolon, exclamation and comma use the width premise. `drop_at` connects an indexed original input byte to the suffix used by `ByteLex.read`.
- `delimiter_law` joins dispatch and cursor/pending construction at every matching byte position. It does not rely on a finite case corpus.
- `after_refines` supplies this derived law and the earlier positive-width progress theorem to UntilAfter's native/reference composition. Alignment, requested-mask restriction and positive provider widths remain explicit premises. This is model composition, not automatic Rust translation or unrestricted callback correctness.

## Driver admission and nonvacuity

`driver_width` derives all three required widths directly from the exact copied AfterDriver.provider definition; `driver_law` quantifies over arbitrary byte lists. `curly_provider_independent` proves that curly opening has width one and the open-curly token for **any** provider.

`driver_zero` and `driver_not_global_progress` retain the obstruction: the driver whitespace family applied to `[59]` has width zero. This family/input combination is not chosen by actual dispatch, but ProviderProgress quantifies over it nonetheless. A future dispatched-family positivity theorem could remove this mismatch; this review does not silently substitute it.

The separate unitProvider satisfies width, global progress and bounds simultaneously, proving the root corollary's provider premises are jointly inhabited. It is a model witness, not a CSS tokenizer. The double-width provider gives a compiled negative witness: semicolon read advances to two instead of one, so both PunctuationWidth and DelimiterLaw fail. No native correctness claim follows from the unit provider.

## Source connection

Searchfox discovery and its sandbox DNS failure/retry are retained. Review uses the complete pinned local sources, not an assumed equality to the indexed revision.

In tokenizer `next_token_unchecked`, comma and semicolon explicitly call `advance(1)`. Exclamation is ASCII, matches no earlier explicit arm, and reaches the default ASCII arm: `advance(1); Delim(b as char)`. Curly opening calls `advance(1)` and `set_at_start_of(CurlyBracket)` before returning CurlyBracketBlock. None of these branches inspects the suffix. The model intentionally projects comma, semicolon and Delim('!') to `other`; curly projects to open-curly and pending-curly. `advance` increments source position and its debug assertions permit these four ASCII non-newline bytes.

The native read requires a non-EOF position in a valid Rust `&str`. The model's indexed-byte premise establishes an available byte mathematically; correspondence of its index with the native cursor, UTF-8 boundaries, machine-size headroom, pending/cache state and the token projection still requires caller/source admission. Nat addition is not a machine-overflow proof. No new native execution was required or claimed; predecessor finite native calibration remains separately scoped.

## Remaining obligations

1. Derive a source-dispatch-specific progress condition for the actual partial driver, or provide a total admitted family implementation. The current global premise is refuted for this driver.
2. Connect actual Rust dispatch and macro lowering to the model for all admitted calls, including UTF-8, machine bounds, valid state, cache and pending-state entry requirements.
3. Retain UntilAfter's callback-program, ownership, mask and alignment restrictions. The bridge is not a universal grammar, public API history, raw metadata or arbitrary callback theorem.
4. The pinned Lean executable is checked by the compiler script. Installed Lean libraries/runtime, compiler correctness and host execution remain external trust; no new toolchain-library verification is claimed.

The initial review-witness compile failed because of an argument-order mistake and attempts to synthesize Decidable for an opaque predicate. Those development errors were fixed in the review extension; the failed log is retained. Root theorem bytes were never changed. All completed owned compiler products were removed after preserving command/output receipts.
