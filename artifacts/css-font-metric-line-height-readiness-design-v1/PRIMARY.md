# Primary-source boundary

Current manual reads use [CSS Values 4 font-relative lengths](https://drafts.csswg.org/css-values-4/#font-relative-lengths), including the `lh` definition and the line-height/font-property exceptions, and [CSS 2 line-height](https://drafts.csswg.org/css2/#propdef-line-height). The first defines `lh` from computed line-height with normal converted using font metrics; direct uses in line-height/font-affecting properties have their specified parent-based exceptions. The second distinguishes computed keyword, number and absolute-length behavior. Modern number-calc implementation is established by the pinned local source, not inferred from CSS 2 grammar.

The existing sealed `css-registered-lh-reentry-spec-trace-v1` supplies the narrow literal-line-height → registered length → selected Weight argument. This design does not infer a normative CSS cycle from an implementation scheduling dependency.

`webspec-index` could not query its read-only database (`attempt to write a readonly database`). Manual current primary reads succeeded; there is no index-wide caller/anchor validation claim.

Searchfox revision `28b7a7bffb5f82828143d9ad63839ad263b598be` discovery:

- [LineHeight conversion](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/values/specified/font.rs)
- [Font-relative length conversion](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/servo/components/style/values/specified/length.rs)
- [Gecko line-height binding](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/layout/style/GeckoBindings.cpp#338)
- [Native final-representation consumption](https://searchfox.org/firefox-main/rev/28b7a7bffb5f82828143d9ad63839ad263b598be/layout/generic/ReflowInput.cpp)

The archived CLI excerpts are discovery evidence. Exact local excerpts in LOCAL-SOURCE.json are the implementation authority because the indexed revision differs in two relevant interfaces. The first attempted local binding filename was ServoBindings.cpp; that read failed without a write. Searchfox identified the actual GeckoBindings.cpp, which is pinned.
