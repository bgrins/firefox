# Scanner provider qualification

This addendum leaves the sealed `css-tokenizer-numeric-admission-v1` and replay receipts unchanged.

The standalone harness compiles the exact `resolved_token_dependencies` body, but supplies a handwritten `SubstitutionFunctionKind::from_ident` shim that maps `var`, `env` and `attr` with the actual cssparser ASCII-insensitive matching macro. The retained enum is copied from the complete native source; its derived `Parse` expansion is neither compiled nor proved by this component. Correspondence of that shim to the derived native parser remains an explicit provider admission.

The seven directly compared numeric observations are produced by complete actual cssparser tokenization and the exact native unit classifier. They do not depend on the shim. The additional whole-scanner control observations do depend on it, particularly rejection of `attr(x)`. No full scanner-provider or declaration-parser proof is implied by calling the helper body an actual native extraction.

All earlier codec, machine arithmetic, metadata, allocator, standard-library and compiler admissions remain. This qualification does not change the numeric lexical theorem, source snapshot or finite observation matrix.
