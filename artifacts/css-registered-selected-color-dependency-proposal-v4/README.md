# Selected-color V4 borrow correction

V3's actual native trial 85310/e7082d/51ecf0/1 failed compilation with E0502 and build exit 2; no browser ran. Independent reviewer 72917/51f609/3abddc/0 verified restoration. Its frozen runtime fd1e00f7 remains failure evidence. This V4 artifact changes only the provider postimage (6002115f); formatted cascade b3c220b1 and value 6624c2a5 remain exact V3 bytes. It retains the combined selected-color/default/image proposal and unchanged 42-case suite; this is not acceptance or a claim of a successful native compile.

Substitution<'a> carries Cow<'a, str>. In particular, the lone-reference fast path can borrow CSS from context.builder.substitution_functions. V3 moved that result across a new function call taking the same context mutably, extending the immutable borrow across the call. The original inline routine allowed the borrow to end before mutation.

V4 introduces an input enum. Ordinary callers pass the original raw VariableValue and AttributeTracker, and the helper performs exactly the old substitute_internal call within its existing exclusive context scope. The existing apply body is unchanged, allowing its original non-lexical lifetime boundary. PreparedCustomKind::Existing instead passes its already-owned static result and never substitutes again. The enum input lifetime is not explicitly tied to the context borrow. The trivial universal path, URL data, property identity (including the attribute route), one tracker pass, CSS-wide handling, error/default path and attr-taint operations remain unchanged.

There is no added clone or into_owned operation. This is a source-level statement that the correction introduces no copy; it is not a claim that the entire substitution algorithm allocates nothing. Existing prepared-value ownership remains unchanged. The native patch applies to the three committed clean originals; the controlled trial must separately restore held provider 2675. V3 and all failed-run artifacts are immutable.

Validation retained here:

- Exact clean patch forward/reverse replay, all three formatted postimages, 16 extracted classifier tests and four killed mutants (438e31 launch / 827dd6 exit 0). These remain isolated classifier coverage, not Stylo type checking.
- Five isolated lifetime tests (d153bf/0): map-borrow mutation boundary, short raw/tracker lifetimes, owned prepared, static prepared/keyword and both error routes. The before analogue fails specifically with E0502; the after analogue compiles. Only the enum is copied exactly; context and computation are test substitutes, so actual Stylo compilation remains required.
- Exact V3 delta, two unchanged postimages, unchanged trivial path and apply body, and no additional clone/into_owned calls (054b7a/0). Owned scratch directories were removed.

Repository Rust configuration is retained from V3; rustfmt from the pinned 1.97.1 toolchain formatted the provider and checked all three candidates. TOOLCHAIN.json is inherited formatter provenance; this successor used that pinned toolchain, not a newly claimed dual-formatter run. No native source, Git/index, application, browser, canonical control or build operation occurred during preparation.
