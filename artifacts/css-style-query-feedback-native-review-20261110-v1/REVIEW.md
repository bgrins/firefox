# Independent native feedback trace review

Native1 supports a narrow positive scheduling observation in two intact per-PID intervals. It does not support an exhaustive absence claim: shared stderr records are visibly interleaved elsewhere, including content-process sequence 2918. Root is preparing an atomic-record rerun. No live source, build, browser or Git operation was performed by this reviewer.

## Native1 manual sequences

All following sequence numbers are native PID 25530. The copied excerpts are contiguous within that PID and checked for unique fields and one CSSFB prefix per record. Their mode labels are contextual associations from the surrounding QF markers; exact cross-stream phase ordering is not needed for the native ordering claim.

| Fixture association | Native evidence | Interpretation |
|---|---|---|
| Opposed | Style call 13, seq43–48 | Two actual timeline changes: fallback to provider and back. First clears start and sets pending; second keeps both timing fields unresolved. Call exits. |
| Opposed | Stale seq55–64; style call15 seq69–74 | Align exit60 resolves start and trigger exit62 clears pending, both at style depth0. A later finite style call performs the two changes again. |
| Opposed | Refresh seq81–92; style call17 seq101–106 | Tick/ready align87 and trigger89 restore timing outside style. Later style work resets it twice and returns. |
| Aligned | Style call74 seq1843–1848 | Same initial two changes with pending reset. |
| Aligned | Stale seq1855–1864; style call76 seq1869–1874 | Align1860 and trigger1862 restore timing outside style; later style call changes provider twice and returns. |
| Aligned | Refresh seq1881–1892; style call78 seq1901–1906 | Align1887 and trigger1889 restore timing outside style; later style call again performs two changes and returns. |

These intervals refute the interpretation that the animation simply never becomes ready. They show actual readiness followed by loss of timing during subsequent provider changes, including the aligned-offset case. There is no ready/align/trigger/tick record at nonzero style depth in these selected intervals. That local observation is not a whole-trace or all-executions claim. Two finite rebindings do not demonstrate recurrence within an unbounded inner style drain.

The raw trace contains interleaved records at JSONL lines566–569,935,3872, including PID25530 seq26 and2918. Whole-trace pairing/absence conclusions must wait for the atomic-record rerun. Raw pointer reuse, non-immutable animation index, timing nullness versus full-state identity, and unproven stdout/stderr phase ordering remain the limits described in the instrumentation review.
