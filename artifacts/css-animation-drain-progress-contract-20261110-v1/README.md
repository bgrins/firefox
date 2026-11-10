# Drain progress: renewal is the remaining contract

The existing descending-phase proof already supplies a useful conditional
termination argument. The missing native condition is causal closure of new
work, especially normal admission of initial or recreated style data. A
successful delivery trace does not supply that condition. No concrete native
infinite recurrence or new browser defect was established here.

## Smallest useful contract

Keep the established finite, stable ranked tree and phases `N(v)` for normal
rebuilding and `A(v)` for application. Productive work consumes a pending
phase; the only regenerative edges are `N(v) → A(v)` and
`A(v) → N(w)` for strict descendants `w`. Requests can coalesce, but their
relevant logical generations must survive through hints and installation or
justified retirement. Finite local processing must cover both cascade levels.

For the native drain, every productive normal admission must consume either
finite initial work or a token caused by a strictly earlier application
phase. Other same-target lifecycle work needs its own bounded budget. It is
insufficient to say that the tree or list of producer functions is finite.
There must also be no unaccounted injection of fresh same-rank obligations,
no recurring style-lifetime replacement outside that domain, and no infinite
administrative execution between productive steps. These are correspondence
premises, not conclusions of the current source audit.

The older `Phases.step_decreases`, `history_budget`, and
`no_infinite_productive_run` already prove the rank consequence under their
precise transition rules. Re-proving a decreasing dirty-count argument would
be weaker and misleading: dirty bits can coalesce, transport can remove queue
entries before installation, and fresh requests can recreate them.

## Explicit non-implication witness

`Renewal.lean` imports a byte-identical copy of the current conservation model
as `Accounting.lean`. At round `n`, all generations below `n` at one target,
pseudo, lifetime, and cascade level have been installed. The state is
conserved, ready, and has no queued, hinted, or in-flight work. Generation `n`
is genuinely fresh. Request, selection, traversal admission, and installation
form a permitted model history ending at the corresponding state for `n+1`.
This construction works for every natural `n`.

`no_round_rank` rules out a natural-valued rank decreasing on every such
round; `same_rank_renewal` shows that an identity-only rank cannot distinguish
successive generations. Nothing is lost or prematurely marked installed in
this witness. Thus conservation, freshness, and actual delivery still do not
exclude unbounded renewal. This makes an existing limitation explicit; it is
not a new scheduler model or evidence that native code follows this history.

The final isolated replay checks 15 theorem declarations and two deliberately
false controls: renewed work has lower identity rank, and previously ready
state makes the next fresh request already settled. Both fail with the
intended kernel `decide` diagnostic. Only standard `propext`, `Quot.sound`,
and `Classical.choice` are allowed by the axiom audit. No custom axioms,
`sorry`, or `native_decide` occur in the accepted proof. Temporary compiled
outputs are removed. Earlier attempts retain ordinary elaboration failures
and one checker diagnostic-string mismatch; they are not successful receipts.

## Exact native admission gap

`NATIVE.json` pins three immutable source files at `037d606ccd27`;
`NATIVE-EXCERPTS.txt` contains the inspected bodies. Searchfox discovery for
`is_initial_style` and `element_needs_traversal` preceded these local reads.
The source gates are concrete:

1. `DomTraversal::element_needs_traversal` returns true for missing data or
   missing primary style before checking `for_animation_only()`.
2. `ElementData::restyle_kind` returns `MatchAndCascade` for no primary style
   before its animation-only branch.
3. `process_animations` skips management work only when animation-only is set
   **and** old primary style exists. Initial styling can therefore reach task
   construction, including animation creation and effect-property updates.
4. `recalc_style_at` clears descendant style data after computing
   `display:none`, using `clear_descendant_data`; it preserves the current
   element's data. This is a concrete lifetime-changing operation, not proof
   that the descendants will be recreated within the same drain.

The new delivery trace's measured admission/installation events all have
`initial=false`. Its 20 successful cohort joins therefore do not test the
exception above. Nor do the source gates alone establish a recurring native
route. Initial child creation caused by an ancestor application may itself satisfy
the strict-descendant phase edge; it is not a cycle. Reaching an unstyled
target once supplies finite initial work; proving
termination requires showing that the same normal admission cannot renew
indefinitely through recreation or another producer.

The next bounded discriminator should target this exception: expose a
previously unstyled subtree under an animation-driven visibility change,
with CSS font animations on its descendants. Require native evidence of
`AnimationOnly`, absent old primary style, and the resulting sequential-task
mask in the same drain call. A normal-only reveal or a pre-styled descendant
does not cover it. Check the relevant display-animation support and entry
route before treating a web construction as a witness. If the route cannot
occur inside the drain, proving that exclusion is equally useful.

For any observed recreation, record the destruction/creation boundary and
keep logical style lifetime distinct from a reused pointer. Determine what
normal-admission cause follows the first application: an already present
initial token, strict-descendant handoff, or a new same-target lifecycle
cause. A source-backed bound for that last cause is the desired contract.
This is a focused coverage gate, not a claim that a runnable reproducer or
native cycle has been found. The task made no native edits or browser runs.

## Running-transition discriminator is already complete

The older boundedness report nominated running transition replacement, but
later experiments executed it. Do not schedule it again as uncovered.
`RUNNING-TRANSITION-ALREADY-COVERED.json` extracts the exact saved results;
`REFERENCES.json` authenticates their assessment and completion records.

| Completed comparison | Original | Candidate |
| --- | --- | --- |
| Certified producer-local combined drain | Final dependent endpoint 30px instead of 60px | PASS, provider and dependent endpoint 60px |
| Producer-only ablation | Same final endpoint failure | Same final endpoint failure |

All four runs recorded old running-transition eligibility, primary/later
reads returning, and stable replacement identity. The failures were final
endpoint delivery failures, not timeouts or repeated replacement. Web-level
eligibility did not instrument the exact native replacement helper. The
combined delivery package already includes that callback. Repeating this
completed A/B work would add less than closing the initial-style gate.

## Replay

Run `python3 -I check.py <new-output-directory>` from this directory. The
checker authenticates the Lean toolchain and copied accounting model,
compiles source-only inputs in disposable scratch, and retains logs and a
result receipt. `run2/RESULT.json` is the first successful complete replay;
the final formatted-checker receipt is identified in `FINAL.json`.
