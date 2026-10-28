# Correct grid transaction receiver

This successor corrects a compile defect in sealed v3. The rollback helper is defined on PropertyDeclarationContext, whereas grid::parse_value receives &ParserContext. V3 incorrectly called context.with_random_index_rollback. V4 calls context.property_declaration_context.with_random_index_rollback, following the existing registered-alternative and seven typed-finalizer call sites. The property_declaration_context field is public and the helper takes &self, so this preserves the shared ParserContext argument passed into parse_grid_template.

V3 remains immutable historical evidence and is rejected as a native candidate. Its author and bounded independent review missed this method-owner mismatch. Rust formatting and patch transport did not typecheck the receiver and must not be presented as compilation evidence. Root identified the defect in bd2b8d/0; the exact captured helper owner, public field and existing calls were re-read in 86679f/0.

Only the receiver and resulting rustfmt layout differ from v3. All three previous parser/value/calc candidate bodies remain byte-identical, and the fourth source still wraps only the enclosing speculative grid-template Result. Existing owned-output, success-retains-index, no-global-transaction and unchanged side-effect scope limits from v3 remain applicable. The sealed ordinary WPT v3 remains unchanged at 26 tests.

Exact four-path forward/reverse/reapply and rustfmt passed 133871/0; private scratch removed. The receiver-only delta was inspected in 53d425/0. Configured native typecheck and candidate browser execution remain required and have not been performed by this package. No source was installed, no original seal altered, and no accepted bug count changed.
