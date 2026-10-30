# Same-element paired observation

The exact authored fixture changed from 1 PASS / 1 FAIL / 1 OK on the restored original to 2 PASS / 1 OK with the existing three-file duration/tri-state candidate. Original88115/77652e/0 and candidate45913/d24784/0 both completed; the candidate browser exit is0. Saved-only independent replay a81795/0, then final frozen replay1a58a4/0 reproduces both raw assessments and the complete two-record collections, and joins the candidate build's exact source and binary pins. This is not a new native acceptance or a new source change.

| Observation | Original | Candidate |
| --- | --- | --- |
| Acyclic contextual opacity: first read, then three passive frames | .75, .75, .75, .75 | .545455, .545455, .545455, .545455 |
| Acyclic later detail reads before/after membership | font22; CSS duration1.375s; opacity effect1000ms/progress.75 | font22; CSS duration1.375s; opacity effect1375ms/progress6/11 |
| Acyclic literal1375 control | .545455 in all four samples | .545455 in all four samples |
| Stepped self-feedback font: first read, then three passive frames | 32, 32, 32, 32 | 16, 16, 16, 16 |
| Stepped contextual later details before/after membership | CSS1s; effect500ms/progress1/time750; font32 | CSS.5s; effect500ms/progress1/time750; font16 |
| Stepped literal500 / literal1000 controls | font32 / font16 | font32 / font16 |

All recorded animation/effect membership checks remain true and the post-intervention held times remain750ms. Timing details are collected after the four first/passive style samples; the report does not pretend a timing API was read at the first sample. The full before/after membership observations and initial calibrations remain in REPLAY.json. These sequential getters are not an atomic internal-engine snapshot.

The acyclic callback now satisfies its unchanged authored first-read oracle: a fixed2s font effect supplies22px, and the contextual opacity duration1375ms gives6/11. The candidate does not add a completion loop, and this result does not resolve the earlier multi-element first-read failures. It establishes this fixture's behavior, not arbitrary dependency-depth completion.

The feedback callback deliberately asserts only its literal controls and acquisition/identity conditions, not a contextual endpoint. Its PASS therefore does not endorse font16 as a cycle policy. The candidate's recorded500ms/progress1/font16 combination differs from the literal500 control's font32. This is a concrete recorded contrast; it does not prove stale composition, a particular task ordering, or a violated self-cycle rule. No alternation or hang was observed in this bounded completed run, but four equal samples cannot exclude changes between observations or prove convergence or a fixed point.

The pinned Blink/WebKit source study (02c31992) complicates the same-element timing oracle: both inspected paths select CSS timing before applying the element's own effects; Blink filters animation longhands out of recascade, while WebKit can recascade dependent computed values after timing synchronization. This is conditional source evidence, not an executed cross-engine comparison or a normative exception. The exact same-element timing-source integration remains an interoperability/specification question. Keep the original FAIL and candidate PASS unchanged as authored outcomes; neither alone establishes a settled landing requirement. Descendant first-read obligations remain a separate question.

Root independently owns current-state verification, restoration and raw-index reconciliation. This analysis reads saved completed output only and does not replace that verification. No new browser/build/native/Git/index/canonical operation was performed.

Frozen candidate0e2168c3 contains57 authenticated regular evidence files. Root verifier28856/e05e64/0 confirms restoration and removal of1,008,605,176 backup bytes; its terminal and raw-only refresh5db08d8d are authenticated here. The epoch changes1c63→81672288 only for raw-index observation4077→e911, with acceptance increment0. This is a saved receipt join, not a fresh independent full-state execution by this reviewer.
