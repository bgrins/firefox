# Existing attr regression controls

The retained `testing/web-platform/tests/css/css-values/attr-security.html` registers **32 subtests**. `collect-identities.js` evaluates only registration/setup against inert stubs and does not execute any test callback, CSS parser or browser. `IDENTITIES.json` retains the exact names, including the existing literal `${url}` in the registered-url case. This is an identity count, not a conformance result.

There are 29 `test_attr` cases whose assertions are conditional on the current custom-property value being empty or `CSS.supports` accepting the substituted property value. Thus an all-PASS result alone does not establish support or executed assertions for every src/string/image variant. The shorthand case and two registered-property helper cases do not use that conditional guard. The focused nine-case proposal uses image-set and explicit computed prerequisites without silent feature skipping.

Relevant retained controls include direct image-set attr, a literal image-set positive control, fallback attr, typed registered string, unregistered string, typed string lists, and chained substitutions. These test general taint propagation, not the equal-payload initial-map and literal-override paths.

No per-file `attr-security.html.ini` existed at inspection. The directory metadata enables `layout.css.random.enabled`, unrelated to these cases. Current StaticPrefList has `layout.css.properties-and-values.enabled`; no CSS attr/modern-attr preference was found. The initial nine-case runner enables the former explicitly. Default exposure is a separate question.

For root's later regression execution, run this unmodified existing WPT with the same binary/source pins and record all 32 exact identities plus harness OK, retaining the conditional-assertion limitation. This supplement does not modify or expand the sealed initial runner. No browser has been run by this worker.
