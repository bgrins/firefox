# Container target-zoom WPT draft

One genuine testharness page with16 named tests and160 planned snapshots. It covers unzoomed size containers, separate unzoomed per-axis containers with a min/max ordering swap, and small-viewport fallback. Every case varies target zoom1/2/.5/1 and checks canonical custom CSSOM, consuming width, scaled rectangles and independent literal-pixel controls. Source dimensions mutate and return to their starting values; fallback also checks ordinary svw/svh.

Suggested eventual WPT path: `css/css-properties-values-api/registered-container-length-target-zoom.html`. Dependencies are only `/resources/testharness.js` and `/resources/testharnessreport.js`, plus standard same-origin about:blank iframes. No new preference or metadata override is requested. ENUMERATION.json contains the exact16 names for an isolated runner. This draft is separate from the existing frozen29-page comparison and does not alter its fixtures or results.

Static node syntax and registration-name enumeration passed94071b/0 without executing test callbacks. The pinned primary help anchors were checked; temporary syntax files were removed. Independent bounded setup/semantic review passed63d147/0. Browser execution remains pending. No live native/WPT files, staged207 files, index, HEAD, epoch or existing artifacts were edited.
