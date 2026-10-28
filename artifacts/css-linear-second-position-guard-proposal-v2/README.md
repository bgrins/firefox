# Formatted linear() endpoint guard successor

The final proposed payload is exactly two paths: easing.rs and the six-test WPT. The both-endpoint guard and WPT semantics are unchanged from sealed v1. V1-DELTA.patch only collapses the adjacent builder.push call and removes its optional trailing argument comma; this is formatter-only, not literally whitespace-only at the token level. native.patch is the complete source delta from the committed base, and fix.patch adds the exact test body.

The WPT remains byte-identical to reviewed v1, including independent literal serialization recovery and no contextual-admission oracle. The original source and v1 package are immutable. SOURCE-PINS.json retains explicit base, predecessor and final hashes.

The root's completed configured Rust check belongs to v1 candidate c72bdb0b... only: runtime RESULT reports success/source restoration/preservation, and build-RESULT exit0. REFERENCES.json binds those actual receipts. V2 has not been compiled or browser-tested; its configured full build remains a future validation. Rustfmt with the actual servo/rustfmt.toml passed1df1e0/0. An earlier check omitted that config and reported unrelated match-arm trailing comma differences; it changed no file. Exact two-path forward/reverse/reapply transport passed in private scratch, which was removed.

This is an inactive candidate, not an acceptance record or source installation. Contextual easing support and the held stepped-function repair remain separate work. No source/index/runtime/epoch changes or accepted ID assignment occurred here.
