# Initial flex clamp reporting: independent acceptance

Accepted one new local diagnostic bugfix. The exact final patch moves only inflexible-item clamp classification after automatic base/minimum resolution, while keeping early freezing in place. It compares the final item's fields. The three-path patch includes the native source, a dedicated chrome test and its manifest entry; research remains separate for a preceding commit.

Root reviewed the native control flow, both regression versions, the source/manifest snapshots and the retained validator. All 72 author files authenticate. Independent raw-log inspection confirmed the original six failures, expanded fifteen failures, repaired144 assertions and full682-assertion/eight-file suite. The exact expanded144 assertion labels correspond before/after; every failing baseline assertion concerns clampState, while used and base sizes pass. Root replay c72976 validates all results, binary continuity, protected earlier edits, unchanged formatted bytes and eight standalone patch application/reversal commands on HEAD and the dirty preimage.

The native build, scoped formatting and lint children all passed. Original wrapper exits caused by process-group drain checks are preserved separately from child outcomes; fresh follow-ups establish absence of all seven owned groups. No test or failed log was overwritten. The full suite ran on the combined local branch; standalone patch application on HEAD does not claim a separate clean-HEAD browser execution.

The regression exercises the privileged ChromeOnly flex diagnostic API. Ordinary WPT cannot observe clampState, and the baseline renders the tested sizes correctly. This is tentatively P3 diagnostic correctness at ordinary sizes, with no demonstrated security or rendered-layout impact. Searchfox's WasMinClamped matches are its getter and the reporting consumer; this supports the diagnostic classification.

The bug was found by auditing native acquisition of the initially frozen flags supplied to the formal caller model, then reproducing it in a browser. It was not found by a Lean disproof and does not invalidate the theorem that preserves supplied initial flags.

Mach's authoritative Herald reviewer is #layout-reviewers. The initial sandboxed metadata queries failed on the existing mach environment lock; escalated read-only queries succeeded. COMMIT-PLAN records the standalone shape and unresolved bug-prefix metadata. No commit, signing attempt, push or Try submission occurred.
