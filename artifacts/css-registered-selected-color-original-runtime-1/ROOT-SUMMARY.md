# Registered selected-color clean baseline

The committed-provider original built successfully and completed 42 callbacks across three pages: 29 PASS, 13 FAIL and three OK page endings. The original five-case reproducer, 23-case preservation page and 14-case cycle/default page are unchanged. This baseline includes the current local branch's accepted fixes; it is not clean upstream Firefox.

Eight failures involve identifier/ColorScheme selection or defaults: the original two union cases, unused fallback selection, an invalid identifier initial, and four cyclic identifier-default cases. Five failures involve registered images: gradient colors, image-set colors, relative lengths, typed-attr lengths and inherited computed images. These are failing cases, not thirteen separate bugs. ROOT-FAILURE-DETAILS.json preserves complete captured observations for each failure.

The image observations distinguish wrong system colors from wrong font-relative dimensions. The target gradient uses 12px/24px while its literal reference uses 20px/40px; the inherited-image case carries 16px/19.2px instead of the parent's 12px/24px. Native cause and repair still require candidate comparison and focused image controls. An image fix must not be silently folded into an unrelated union fix.

Contextual initial-value cases remain conditional source-preservation probes. Observed successful registration does not establish normative permission for those registrations; the source/spec review is separate.

Owner: 57577/eb6f51/d1cec3, exit 0. Independent replay/restoration review: 18962/2e16ba/4cb7ca, exit 0. Build exit 0; browser exit 1. The native working diff was empty during original build/test. Build and browser metadata/binaries join at ecfe313d582a with committed provider8a4; the restored20ab application and held2675 provider are distinct roles.

All original source/application state was restored, staging stayed empty, owned processes/profiles were absent, and the verified 1,008,605,176-byte backup was removed. Only raw-index bookkeeping changed afterward, recorded in ROOT-EPOCH-REFRESH.json. No candidate was installed, native fix accepted or commit created.

| Cases | PASS | FAIL |
|---|---:|---:|
| Original reproducer |3|2|
| General/default preservation |16|7|
| Cyclic-default preservation |10|4|
| Total |29|13|
