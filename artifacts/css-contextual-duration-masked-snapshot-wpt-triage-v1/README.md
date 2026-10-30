The completed candidate WPT phase has **9 PASS, 4 OK, browser exit0**, versus the frozen original's **6 PASS, 3 FAIL, 4 OK, browser exit1**. Its saved comparison gate remains **false**, with exactly `regression identities/status/expectations/intermittents changed`. This external triage does not rewrite that result or reinterpret it as a strict comparison pass.

| Authored callback | Original | Candidate |
| --- | --- | --- |
| getAnimations processes a masked font change before retained effect timing is queried | FAIL | PASS |
| Changing a masked authored font updates contextual animation duration on the first read | FAIL | PASS |
| Changing an inherited host variable updates masked ::before duration on the first opacity read | FAIL | PASS |
| Element and ::before outline, same-value, script-duration controls (six callbacks) | PASS | PASS |
| Four page endings | OK | OK |

The observer policy declares zero targets and nine regression controls. Consequently all nine callback signatures plus four endings belong to its 13-item equality signature. The three intended improvements change status, remove the explicit expected-PASS field, and remove failure message/field. Effective expected status remains PASS and intermittent fields/lists are unchanged. This is exactly why the equality gate fails. All six passing-control signatures and all four ending signatures are byte-for-byte equal as normalized by the unchanged assessor. No failure or changed expectation is hidden by the triage.

Saved-only replay uses each original/candidate assessor wrapper with its own stored policy, phase application metadata and actual browser exit. Both exact assessment objects reproduce, ordered lifecycle/roster/infrastructure checks pass, and candidate comparison retains its sole original error. The complete frozen original manifest b38215f9 is authenticated. Eight copied resources, identical manifest and metadata are checked against their pinned bodies for both phases. No metadata expectation was changed to produce these results. The reporting script writes only this external report; it does not run an owner, current guard, browser, Git or process command.

These are authored WPT outcomes for the snapshot-admission proposal and final authored32/composed32 inputs. They do not establish partial24 behavior, pre-own timing policy, custom-property taint preservation, arbitrary descendant completion, performance, or new native acceptance. PASS callbacks do not provide archived private numeric trajectories. Initial preservation controls are observational rather than a separate proof of normative initial timing. Root owns candidate terminal/restoration verification and final runtime freeze; this phase-only report makes no claim about their completion.

Actual saved replay 284d88/0 established the phase delta; final replay adds authentication of the original frozen package. An initial replay attempt d867a2/1 stopped because it used the candidate wrapper's descriptive oracle text for the original assessment. Using each unchanged wrapper resolves that descriptive mismatch (f823a6/0); no runtime assessment changed. Future root verification must preserve the false strict gate while separately reporting the nine WPT passes and restoration result.
