# Standalone nowrap paired native outcome

The candidate passes all 169 target callbacks, improving the original's 133 PASS / 36 FAIL. The original 133 passing target signatures and its OK ending remain unchanged. The regression lane retains 637 PASS / 83 FAIL callbacks, 17 OK harness endings and four PASS reftest endings. Its 737 non-reftest-ending signatures are exactly unchanged. Four reftest messages differ solely in the two role-specific URL ports; the bounded comparison below establishes all 741 regression signatures equivalent under that transport-only allowance.

The saved owner and assessor gate remains **false**. `OBSERVATIONS.json` retains it separately from the **true derived observation gate**; no owner, raw stream, assessment or runtime file was changed. This report supports publication consideration for the isolated patch, not a claim that all regression tests pass or a native publication action.

## Source, build and observation binding

`review.py` authenticates the frozen runtime and active owner payloads, replays all four complete WPT lanes through the owner's assessor, and checks each role's own build, source, binary and application-metadata binding. The sole overlay is `dom/base/nsLineBreaker.cpp`, c8b2d4f760e6976bb954eae77983da6b5ea795cdac6ac03db214680e5bd745ea → a87f4210c39f99f27e78df7827b2836362098ff7cd5290a88660d5f943052e03. Both builds use HEAD 10e043823f5fb60317be96ada71e8fd39794e100. All staged fixture/resource/manifest/metadata pins and required absences are checked against the owner policy; no expected-FAIL suppression or new preferences were introduced by this review. The suite retains existing regression metadata and failures.

There are 889 callbacks and 22 page endings (911 signatures) per role. All original passing callback signatures are preserved. The original failures remain visible in the report, including the 83 unchanged regression failures. Candidate target failures are zero. This is the exact 169-case fixture and 21-page regression suite run by the owner; no browser rerun or substitute fixture is inferred.

## Four-message port correction

`ports.compare(runtime, policy, original, candidate, signature)` is a read-only entrypoint usable by the publication gate. It accepts only the four explicitly named reftests. Each manifest must specify the exact test/reference pair with `==`. The per-role command and upstream manifest configuration must point to that archived role's staging tree; the raw events must equal the supplied assessor rows/endings. The helper checks complete assessments with no infrastructure errors, the one exact known regression-comparison error, exact cardinality and unique identities.

Each message must match the full literal grammar `Testing http://web-platform.test:PORT/TEST == http://web-platform.test:PORT/REFERENCE\n`. Both ports must agree, paths/host/scheme/relation must match, and each result must be PASS with expected PASS and no intermittent outcomes. The port is bound to that role's raw wptserve startup and shutdown records, with the same server PID and the test time strictly between them. The recorded startup text says **https**, while shutdown says **http** and the reftest messages use **http**. The helper binds these exact observed strings and the server process/port; it does not infer general HTTP/HTTPS equivalence or normalize schemes.

Only the two numeric URL ports in those four messages are replaced with a role-port token. All other existing signature fields remain exact, including status, expectation presence/value, intermittent presence/value, message presence and non-port text. Original port 56434 and candidate port 57484 are retained in the report. The full review also requires the saved behavior's only errors to be the known regression comparison error plus those exact four ending differences. Raw failures are not converted to PASS.

`check_ports.py` rejects 14 mutations: status, expected value/presence, intermittents, path, host, scheme, relation, added text, an unbound port, absent startup, changed server PID, changed manifest relation and an unrelated callback message. This is a narrow correction for this saved pair, not a generic log normalizer.

## Restoration authority and actual checks

Owner terminal: 6129 / a1b368 / d6a86a / exit 0. Result SHA: 94bc8f2ebf2f29c8a03e1f0db4828d6ad46c2a1cc1cd5d41595a508edb7da6a0. Owner restoration, unchanged controls, empty staging and removal of the 1,008,605,176-byte owned backup are recorded.

Our review is saved-only. Independent **live** restoration authority is root's separate audit 37858 / e162d0 / 56b2d4 / exit 0, report SHA e8571829573e6b544d774478247c31c8aee16a24fa5b3811b7459ec93db22e6e. Its exact script/report/terminal are pinned; the report's eight absent process groups are joined to this pair's build/wake/WPT receipts. It independently verifies source/binary/app/extras, flags, controls and backup cleanup. Raw index bytes changed without semantic index change; canonical refresh is separate and is not performed by this package.

Actual saved replay c6002d/0 authenticates 256 references. The final 14-mutation check also passed in that call. Earlier successful replay da9cda/0 preceded the root-live join; the first added join failed on a guessed backup-field name (0b067f/1), retained in REVIEW-FINAL.log, then the schema was corrected and replay passed bd68ef/0 and c6002d/0. No native build, live check, source/Git write or browser run was performed by this review.
