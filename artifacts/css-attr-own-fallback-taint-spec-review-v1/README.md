# Taint on attr()'s own literal fallback

The current normative text requires the selected fallback result to be attr-tainted. The inspected primary discussions do not establish an intentional exemption for stylesheet-authored constants. This identifies a source-policy mismatch at the retained and synchronous substitution boundary, not a demonstrated browser leak or a new accepted fix.

Assume valid declarations, supported `image-set()`, no competing cascade or animation, and these two cases:

```css
background-image: image-set(attr(data-missing raw-string, "https://example.test/x"));
background-image: image-set(attr(data-bad type(<number>), "https://example.test/x"));
```

`data-missing` is absent; `data-bad` contains `not-a-number`. The fallback contains no substitution functions. These are attr's own fallbacks, not a var fallback containing attr.

1. [Replace attr, step 3](https://drafts.csswg.org/css-values-5/#replace-an-attr-function) sends the absent case to FAILURE. The invalid typed case reaches the same branch through step 6.
2. Step 7.3 says: “Substitute arbitrary substitution functions in second arg, and return the result.” The literal string therefore becomes this attr invocation's returned value. Its lack of nested attr calls does not make it a different producer.
3. [Security](https://drafts.csswg.org/css-values-5/#attr-security) taints values produced by attr. The separate propagation rule covers values derived through other substitution functions; it does not limit the initial attr rule to successful DOM attribute reads. Neither branch has an exception for the selected fallback.
4. [Images 4](https://drafts.csswg.org/css-images-4/#image-set-notation) specifies: “Each <string> inside image-set() represents a <url>.” Thus the tainted string reaches a URL use, which makes the declaration invalid at computed-value time. In this isolated background-image case the expected computed value is `none`.

The literal URL without attr is a separate valid control. An attr fallback containing another attr is tainted independently, and would not discriminate the missing outer-fallback marking. A literal non-URL fallback can remain usable: taint is not universal invalidity.

Prior-art scope:

- [Issue #5092](https://github.com/w3c/csswg-drafts/issues/5092#issuecomment-1755809447) proposes marking strings produced by attr and prohibiting their URL use. It provides no explicit own-fallback exemption.
- Merged [PR #11218](https://github.com/w3c/csswg-drafts/pull/11218) clarifies whole substitution-value propagation, rejecting partial custom-property tainting. It does not decide that constants returned by attr are exempt.
- [Issue #13946](https://github.com/w3c/csswg-drafts/issues/13946) concerns banning the `<url>` syntax component and possible `<image>` equivalents. That syntax debate does not exempt a string used in image-set, and does not answer own-fallback taint.
- [Issue #13742](https://github.com/w3c/csswg-drafts/issues/13742#issuecomment-4614701512) distinguishes uninterpreted custom-property tokens from later URL interpretation. Merely observing the serialized fallback string in a custom property is therefore not a taint correctness test.
- Saved upstream `attr-security.html` tests direct attr strings, registered-property propagation and var fallbacks containing attr. Its fallback section does **not** exercise attr's own literal fallback. `attr-notype-fallback.html` checks ordinary content fallback rendering; `attr-all-types.html` has non-URL typed-fallback cases. Neither establishes a taint exemption. The inspected upstream tests were read, not run.

The exact integrated-v2 provider confirms the boundary raised by root: `invalid_primary` creates an ordinary fallback chunk; a literal chunk produces `attr_tainted=false`; `SubstitutionReferenceStage::Fallback` forwards that result without marking it. The legacy `substitute_one_reference` fallback tail similarly calls `do_substitute_chunk`; its literal fast path returns default false taint. Successful primary attribute conversion does mark its result, so the omission is branch-specific. `SOURCE.json` pins these exact excerpts and the sealed provider. No claim is made here that a later caller cannot add taint; no native/browser URL result was measured.

A focused follow-up should assert the returned taint/range for each of the two selected literal fallbacks, then verify the ordinary URL sink separately. A Pending/resume variant should preserve that same taint result. Keep literal-without-attr and nested-attr fallback controls distinct. No implementation or test mutation was performed in this package.

`trace.log` records four untruncated routes at depth 9; the relevant one is FAILURE step 7.3. Taint is a normative value classification rather than a separate algorithm call, so the final classification-to-URL join is read directly from the two clauses. Six anchors resolve in `ANCHORS.json`. Bounded public issue/code searches are retained; their lack of an exemption is supporting scope information, not the basis for the rule.

**Verdict: REACHED** — the current attr replacement and taint clauses cover its own selected literal fallback, making both specified image-set declarations invalid at computed-value time. No inspected resolution overrides that rule with a safe-constant exemption.
