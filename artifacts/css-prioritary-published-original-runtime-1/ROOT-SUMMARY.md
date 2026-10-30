# Fresh published-source baseline

Built source at signed HEAD `42cc9997e71cabd8afbcceb3ef6bc73675413f70`. The build exited 0 and compiled style, geckoservo and gkrust. The existing Mach progress-monitor `KeyError: export` remains in the log; it did not determine the build outcome.

All 77 callbacks and 12 page endings were acquired and independently replayed: ordinary 59 PASS / 9 FAIL, forced colors 0 PASS / 3 FAIL, Appearance 5 PASS / 1 FAIL. Overall: 64 PASS / 13 FAIL / 12 OK. All eight published color/image WPT cases pass. The fresh 64-case PASS set, 24 target states and eight published-case states are in ROOT-REVIEW.json. Real Zoom capture replayed; its numerical policy verdict remains null.

Full source/application restoration, ownership, flags and process cleanup independently verified. The 1,008,605,176-byte backup was removed by the successful owner. Raw index bytes are unchanged, so no canonical epoch refresh was performed. The restored old application remains `built:false` relative to current source. This baseline is not a new bugfix acceptance.

The forced-colors lane exactly matches the historical ORIGINAL baseline's five strict signatures. An earlier provisional root update incorrectly compared against the experimental V4 CANDIDATE's two passing cases; that comparison was corrected. No A+I-introduced forced-colors regression is shown.
