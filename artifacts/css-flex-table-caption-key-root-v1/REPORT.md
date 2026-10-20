# Root acceptance: containing-block size in flex measurement cache

Accepted within the scope in ACCEPTANCE.json. The exact standalone patch adds
one LogicalSize member and initializes it from the actual ReflowInput containing
block. Existing default equality includes both coordinates. The patch contains
only Gecko and the 16-subtest WPT, with no padding-key dependency.

Root inspected the complete cache class, measuring early return, cross-size
consumer, final-reflow predicate and table wrapper's auto-size path. An auto
caption can hide a changed inner percentage basis behind an unchanged wrapper
computed size. A measuring hit leaves HadMeasuringReflow false and can feed an
old cross size into a successful final skip. The added input rejects that first
reuse; it does not change final-skip policy or claim to make every input complete.
The supplied fresh-provider theorem is conditional, not a proof that copying a
key itself computes current CSS geometry.

Both release and project discovery reproduce four discrepancies in16 cases.
The final WPT pair fixes those four and preserves12 passes. All354 additional
subtests pass; eight existing reftest outcomes remain sevenPASS/oneexpectedFAIL.
Both builds and source restoration passed. Actual-path format made no changes,
WPT lint passed without warnings, and reviewers resolve to #layout-reviewers.
Independent source/runtime review passed and its checker was replayed by root.

Root authenticated the sealed proof source and ran a fresh manifest-only
relocation:19audits,4kernel falseclaims,384 native cases in15runs and three
compiled mutations pass. Root read the source/admission mapping and all model
modules. Complete cache classes are extracted, but native primitives and the
successful fresh callback remain supplied. Same-key external change remains a
negative witness. Full F1–F16/F11/F12 and callback/lifetime freshness stay open.
Terminal compiler products were removed with hashes and sizes retained.

The standalone patch was independently applied and reversed on the retained
upstream source. Runtime used the shared combined tree, and no upstream browser
or performance-neutrality claim is made. This key costs one LogicalSize and may
cause conservative misses. Commit signing is still blocked; no commit or push
is represented by this acceptance.
