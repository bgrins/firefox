# Native URL state and raw-slice bridge

Status: active producer plan, not a frozen proof or acceptance record. The accepted URL provider capsule remains unchanged. This work addresses precisely its two open native bridges.

## Representation and invariants

Model the actual mutable fields: `position`, `current_line_start_position`, and `line_number_and_block_type`. The line-start field must retain modulo-2^32 arithmetic: a four-byte intro deliberately wraps zero to UINT32_MAX. Do not replace this with an assumption that the field never underflows. Relate the packed line field to `4 * line + block`, with low block bits preserved and line-add headroom explicit.

The independent reference remains raw-prefix observation in UTF-16 columns. Use a relation between stored native state and reference state, deriving column from `position - current_line_start_position + 1` modulo 2^32. Only the final equality with an unbounded reference column needs a column-range premise. Position arithmetic, packed line overflow, codec, heap and compiler boundaries remain explicit.

## Implementation sequence

1. Bind complete native state accessors and helper bodies. Prove each actual assignment sequence preserves the relation: ordinary advance; UTF-8 intro/continuation; known byte; whole-character consumption; CR/LF/FF including paired CRLF; line-number update and source-location projection.
2. Model the complete bad-URL mutable loop. Derive consumption and state from helper transitions. Capture the raw end before advancing a genuine closing parenthesis and at EOF; prove these captured endpoints rather than applying an observer to an assumed prefix.
3. Model the actual escape helper's state path: bounded hex loop, optional whitespace/newline consumption, replacement/NUL, whole-character path and EOF. Compose inherited decoded-value results without using them as a metadata oracle.
4. Model borrowed and owned URL loops and whitespace-end handoff. Preserve the original `start_pos` through allocation and recovery. Derive state, exact consumed source, EOF and closing behavior branch by branch.
5. Compose initial whitespace bulk preparation / quoted rollback and the complete body machine. Derive native `slice_from` ranges from an explicit full-input/remaining-suffix invariant. Connect raw BadUrl payload to actual captured start/end, including recovery after a copied prefix, invalid byte, escape, whitespace and EOF.
6. Source-only native replay exposes the three real state fields and captured raw spans, retaining the predecessor's fixed cases. Add a targeted case only if a concrete bridge gap demands it: the predecessor has no bad-URL escaped-close-at-EOF raw-span case, so that endpoint needs one source-level witness. This is verification coverage, not a new bug claim.
7. Kernel audit, semantic mutants, exact complete-source inventory, closed source-only checker, relocated replay and independent review. No claim of all CSS, all public parser histories or compiler/heap verification.

## Immediate source findings

- `current_line_start_position` intentionally wraps for astral characters; existing native `utf16_columns` tests explicitly cover this. A no-underflow assumption would exclude a reachable ordinary path.
- `ParserState` packs the block discriminator into the low two line bits. Newline updates preserve these bits only within the stated machine arithmetic domain; model that field rather than a separate unexplained line counter.
- `consume_bad_url` slices before consuming a genuine close, but slices at the final cursor on EOF. An escaped closing parenthesis consumed as a pair is therefore retained in the raw payload when EOF follows.
- No new observable defect is currently established. Existing committed bad-URL and depth repairs stay in the baseline.
