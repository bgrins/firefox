# Clean-provider animation-taint candidate

The four-source animation-taint candidate built successfully and completed 125 callbacks across 18 pages: 124 PASS, 1 FAIL, and all 18 page endings OK. Against the separately built clean-provider baseline (105 PASS / 20 FAIL), 19 failing callbacks now pass. All 105 previously passing callbacks retain their full result signatures. The remaining typed-attr consuming-property-context failure also retains its full signature.

The exact-equality comparison gate remains false because the failure cohort changed; the underlying result rows and comparison diagnostic are preserved. This complete observation does not accept a native fix or resolve the broader animation-taint ownership/lifetime specification questions. The candidate selects active animation provenance; it is not a complete lifetime-policy implementation.

The trial used the committed provider as its patch base, independently of the held provider edit. Build and browser source/binary metadata were joined at HEAD ecfe313d582a. Afterward the held provider and all other source preimages were restored with their original identities. The original application was restored, owned processes/profiles were absent, and the verified 1,008,605,176-byte backup was removed. Only raw-index bookkeeping changed; semantic staging and HEAD were preserved.

Owner: session 97217, launch 0b392d, terminal 4b7236, exit 0. Independent replay/restoration review: session 27191, launch b5b1ec, terminal a55877, exit 0. ROOT-REVIEW.json records the complete cohorts and restoration evidence; ROOT-EPOCH-REFRESH.json records the subsequent raw-index-only update.

| Cohort | Original | Candidate |
|---|---:|---:|
| Passing controls |105 PASS|105 PASS, full signatures unchanged|
| Research failures resolved |19 FAIL|19 PASS|
| Typed attr context |1 FAIL|1 FAIL, full signature unchanged|
| Page endings |18 OK|18 OK|

No new accepted fix or commit was created by this trial.
