# Quoted EOF fallback endpoint

The pinned local browser crashes with an out-of-bounds Rust string slice in
`do_substitute_chunk`. The reported buffer is `var(--absent, "example")`, and
the rejected byte index is 25. No native changes were applied for this run.

Source review identifies a mismatch between two existing operations:
`parse_declaration_value_block` records reference endpoints using original
source length plus missing closing characters; `VariableValue::parse` then
removes a terminal backslash before appending the closing quote. Enclosing
references still refer to the one-byte-longer buffer.

The initial test includes closed and missing-quote controls followed by an
escaped-EOF fallback. The process crash prevents the harness from retaining
individual subtest results. The separate semantic probe reruns both controls
successfully, so this receipt claims one test crash, not three failing cases.

Endpoint repair must follow the actual deletion for every enclosing reference,
including nested fallback references, while preserving earlier sibling ends.
The even-backslash and escaped-terminal-quote value errors are separate repair
targets. This endpoint regression should use odd terminal backslash runs so it
does not depend on either semantic repair.

This is a shared experimental macOS build, not a pristine upstream or release
browser measurement. Source/configuration/resource/binary hashes are stable
across the run. The finding arose from source review while extending tokenizer
admission, then browser reproduction; a completed Lean proof did not discover
it. Native repair, independent review, paired browser validation and separate
native/WPT commits remain outstanding. No accepted-fix increment is made.
