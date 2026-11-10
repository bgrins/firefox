# Reviewed vocabulary and state domain

The development algorithm is CSS Syntax's consumption of an escaped code point. Consume-number is held out from this version's grammar development until a recorded freeze. Prior exposure is recorded in PROTOCOL.json; this is not blind evaluation.

## State and types

`Program α` is a typed Lean effect IR. Its instructions return a value, read one optional scalar, scan a bounded maximal prefix, skip at most one matching scalar, raise a parse-error flag, branch on a Boolean, or sequence two programs. The interpreter is total Lean code. The scanner's budget decreases on each recursive step. Continuations and pure expressions are Lean functions: this is a higher-order embedded IR, not a first-order serializable bytecode or a verified Python compiler.

State contains the next unread `List Char` and an accumulated Boolean parse-error flag. The backslash is already consumed. Reading removes the head, or returns EOF (`none`) without changing an empty list. No distinct current-input register is modeled: the first read binds that observation, which is used for the literal result; subsequent reads operate on the residual list. `execute` starts the flag at false and returns a scalar, residual list and error flag together. This is a chosen abstraction of CSS's input machinery, not a proved refinement of a native tokenizer cursor/reconsume implementation.

`Char` contains Unicode scalars, not raw UTF-16 code units or surrogate code points. CSS preprocessing must already have handled encoding/DOMString conversion, CRLF, CR, form feed, null and surrogate replacement. The copied `CssInput` model covers normalization of scalar lists; it cannot itself model surrogate replacement because its input is already `Char`. The spec-facing caller also requires a valid escape after the backslash, so an initial LF is excluded. EOF is allowed by this caller predicate. The core executable is total on all scalar lists, but its extra behavior outside the caller domain is not a CSS conformance claim.

## Extraction and interpretation

The source interface is accepted only when its entire reviewed introduction matches the escape contract. The whole normalized operative body must match the supported instruction shape; extra or unknown clauses are refused. Inline markup is stripped while preserving text. One exact explanatory note and one exact WPT metadata block are retained and classified manually as non-operative; unfamiliar metadata is refused. The section and body have byte spans, and each resolved definition has its own byte span. Individual instruction spans are not yet recorded.

The ordered body recognizes initial consumption, a hex/default/EOF case split, maximal additional hex consumption with an extracted bound, one conditional whitespace consumption, hexadecimal interpretation, three invalid-value conditions, replacement returns, EOF error and literal return. Python emits a typed Lean program from the extracted parameters. It does not call the existing reference parser or its helpers.

The CSS source supplies the digit/hex ranges, whitespace definition, maximum code point, additional-digit limit and replacement code points. A separately pinned Infra source supplies leading/trailing surrogate ranges and their union. The extractor checks adjacency before representing that union as one interval. Unicode names and displayed glyphs are not independently validated against their numeric values; the source bytes are pinned.

The following meanings are authored manually and reviewed, not mechanically proved from English: inclusive ranges, maximal bounded scanning, exactly one conditional terminator, base-16 positional arithmetic and letter digit values 10–15, inclusive “or”, invalid-value replacement, EOF/error behavior, ordered branches, current/next observation mapping and the initial error flag. A one-element bounded scan implements optional whitespace consumption. Generated pure Lean predicates/arithmetic and the IR interpreter acquire meaning from Lean; the prose-to-IR boundary remains unverified.

The entire parsed body is deliberately narrow. This version has no source vocabulary for numeric tuple results, mutable token flags, decimal/exponent accumulation, unbounded scanning, or general calls to other specification algorithms. `Program` can express more than the Python source grammar recognizes. Unsupported interfaces must not select a familiar reference implementation by algorithm name.

## Checked correspondence

Read-only reference snapshots predate this experiment. The bridge independently proves classifier/arithmetic agreement, bounded scanning agreement, optional terminator agreement, and complete result agreement; then it connects the generated result to the existing `Escaped` relation. That relation describes character, remaining input and EOF error together. Caller-ready and preprocessing theorems expose the spec-facing domain rather than silently assuming all scalar inputs are valid calls.

The freeze includes this file, translator, IR interpreter, protocol, source manifests and library manifest. After freezing, consuming-number evaluation must use those exact rules. Proofs/driver development does not authorize changes to the frozen semantics. A new interpretation requires a new artifact/version.
