# Frozen paired pending/posting observations

The sealed paired helper authenticated both frozen runtimes and exactly replayed TRACE-INDEX (654475/0). Original owner52738/320f89/0 passed; candidate owner12619/d85f20/1 failed. Root separately verified restoration and removed the owned backup (candidate65323/7496ff/0). These outcomes remain unchanged.

| Derived result | Instrumented original | Instrumented candidate |
| --- | ---: | ---: |
| Callbacks / page ending | 2 PASS / OK | 2 FAIL / OK |
| Calibrated acquisition | true | false |
| Events / fixture labels | 385 / 10 | 887 / 10 |
| Parser errors / cap markers | 0 / 0 | 0 / 0 |
| Bounded witness intervals | 0 | 13 |
| Dispatch attempts | 16 | 6 |
| Post hints / consumed-removal boundaries | 26 / 26 | 28 / 28 |

Both selected streams are raw.jsonl, with continuous process-local sequences and no missing IDs. Raw and formatted logs were not merged. This verifies the recorded stream under the logger contract, not coverage of every native operation.

The candidate reproduces both fixed-2s override font failures. Coupled reports2000ms/progress.375 but renders22.85px/opacity.428571; zero-start reports2000ms/.375 but renders0px. Original renders22px/.375 and12px. Literal2s measurements remain correct in both, with retained animation/effect identity. Candidate assertions stop at the font errors; later literal measurements are not separately passed assertions.

The13 candidate intervals span six target keys. Repeated intervals can share one deferred seed: these are not13 independent stalls or bugs.

| Label | Request/set/defer sequences | Outside Layer request/coalesced pairs |
| --- | --- | --- |
| coupled-seek |128/129/130|139/140,143/144,151/152,155/156|
| coupled-override |395/396/397|406/407,410/411|
| zero-start-passive |516/517/518|529/530|
| zero-start-seek |563/564/565|574/575,578/579,584/585|
| zero-start-outline |622/623/624|633/634|
| zero-start-override |761/762/763|772/773,776/777|

These intervals are in PID93059/cascade0, with element/pseudo/identifier keys separated in SUMMARY.json. In coupled-override395–397, a Standard request sees present0/bit0 during Servo, sets bit1 and defers. Later406–407 and410–411 are Layer requests with present1/bit1 and Servo0/PreTraverse0. There is no intervening logged dispatch attempt, hint, removal or clear for that key. Zero-start-override761–763 and772–773/776–777 shows the same bounded pattern. This particular pending/coalescing sequence is now observed, rather than merely predicted; it does not establish the complete stale-rendering cause.

Original also defers and coalesces, but has no qualifying interval. Its coupled-override147–149 seed is followed by hint164/removal167. A new outside Standard request168–170 attempts dispatch before Layer171–172 coalesces. Isolated coalescing is therefore insufficient evidence. Candidate additionally logs288 pre-skip-no-shell eligibility events with unspecified cascade; their count alone proves neither consumption nor failure.

The model mapping still requires:

- Stable native table identity and coverage of uninstrumented removal, destruction, adoption or address reuse. A full-key recorded interval is not a universal lifetime proof.
- Evidence for abstract posted=false beyond an absent dispatch marker: previously queued work, other wake sources and actual restyle roots are not fully logged. Dispatch markers precede PresShell calls and establish attempts only.
- A refinement argument for exitWithoutDrain. Inside-Servo followed by outside/prior-bit1 supports the premise's motivation but does not log traversal exit or every drain.
- Separate treatment of the deferred guard's Servo/PreTraverse disjunction and **styleRefresh, which was not logged**. Servo0/PreTraverse0 does not establish outside-style-refresh safety or justify immediate posting.
- Effective timing-change and composition correspondence. A Layer request is not necessarily an appliedGeneration increment; WillCompose is preparation, and removal does not prove fresh composition. IDs align record kind/role only, not exact JavaScript phases or model steps.

The trace supports further investigation of pending-work consumption. It proves neither native causality nor a safe repair, fairness, convergence or self-feedback cycle. The two fixed-control failures remain concrete candidate regressions independent of self-dependent numerical policy. No native/model acceptance or coverage increment follows.

REPORT.json retains the complete derived report; SUMMARY.json contains counts and all intervals. Original manifest: fb2fb7612b8f38b883f103b335389edb1cc9888741322d4def291147927892ab. Candidate manifest:1b03737814f322543b04f8fc316c4419fc84eb17e6fbc03fb7c20c9f4752045c. No runtime or live state was modified.
