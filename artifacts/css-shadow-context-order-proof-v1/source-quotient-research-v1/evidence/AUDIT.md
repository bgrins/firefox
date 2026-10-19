# Declaration-block identity construction audit, in progress

This is additional source evidence for the open C7/C10/C13 quotient. It is not a proof that declaration-block pointers uniquely identify all semantic occurrences. The frozen formal input sources and native candidate packages are unchanged.

## Reviewed construction and mutation chain

- `NestedRuleParser::parse_block` creates a fresh locked declaration-block Arc for each parsed StyleRule. `StyleRule::deep_clone_with_lock` allocates a fresh Arc containing a cloned block.
- Nested declaration rules produced by `flush_declarations`, the declaration fallback of `CssRule::parse`, and `NestedDeclarationsRule::deep_clone_with_lock` likewise allocate fresh block Arcs.
- `Servo_StyleRule_SetStyle` and `Servo_NestedDeclarationsRule_SetStyle` accept and retain an existing block pointer. Those functions alone do not enforce block uniqueness.
- Searchfox caller discovery identifies `CSSStyleRuleDeclaration::SetCSSDeclaration` and `CSSNestedDeclarationsDeclaration::SetCSSDeclaration` as the respective C++ setters. Their inherited `nsDOMCSSDeclaration` operations supply either a freshly parsed CSS-text block or `EnsureBlockMutable(olddecl)`.
- `EnsureBlockMutable` retains the existing pointer when mutable and calls `Servo_DeclarationBlock_Clone` when immutable. The clone and parse entry points allocate new block Arcs. The reviewed ordinary CSSOM path therefore retains the rule's own block or substitutes a fresh block; it does not deliberately take a block from another rule.
- Both C++ declarations invoke stylesheet `WillDirty` before modification and replace their raw block after stylesheet cloning. This is consistent with allocation lifetime preservation; a complete ownership/locking and snapshot proof is still required.

## Limits

These observations strengthen the reachable-source admission argument, but do not replace the conservative grouping proof. Derived `Clone`, stylesheet sharing/adoption/import occurrences, generated providers, all foreign-call entry points, and native rule-tree identity still need complete closure. A shared StyleRule can have several selector occurrences; rule-block identity is not a unique matched occurrence. No declaration-level deterministic-action premise is valid: logical/physical aliases and mixed importance can give different actions under one key.

The existing OccurrenceDeletion and CombinedRollback theorems operate on semantic identities. Mapping those identities to block address plus exact unimportant priority remains unproved. The parser and CSSOM facts above must not be promoted to universal uniqueness without closing every constructor and mutation path.
