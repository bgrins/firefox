# Collection snapshot lifecycle model

This isolated extension checks new lifecycle and admission obligations of the seven-file snapshot proposal. It does not repeat the predecessor's finite-input-history synchronization theorem. `MaskedBaseInput.lean` is imported unchanged; only its `Owner` type is reused. No canonical library, native source, browser or Git state is changed.

The predecessor assumes an initialized, truthful old input and applies `timing(input)`. The native proposal instead caches a base-duration list, can encounter an absent or unsampled collection, prioritizes existing full-update reasons, and still passes composed timing to the manager. Its cache therefore cannot establish the predecessor's synchronization premise. `fresh_cache_does_not_certify_applied_base_duration` makes this difference concrete: cache 1000 and applied 2000 are compatible with a successful commit. These numbers illustrate the model; they are not a new browser result.

`Collection Key` has an optional sampled key, an applied duration and field ownership. An absent outer `Option` means no collection; an absent inner sample means an existing but unsampled collection. `Key` is arbitrary with decidable equality, abstracting the complete typed duration list without proving its native encoding or CSS evaluation. `Reason.full` always dispatches the manager path. `Reason.verify` skips absence and an equal known sample, but dispatches unknown or unequal samples. `step` performs a single synchronous operation; it has no deferred captured input or interleaving.

`commit` models the outcome of that manager path. Cancellation removes the collection. A surviving collection records the supplied key. The independently supplied composed duration is applied to CSS-owned or replacement effects; a retained script-owned effect keeps its override. The `survives` and `reusesEffect` outcomes are explicit environmental inputs, not proven properties of the native builder. Here replacement means creation/replacement of a CSS-owned effect by the CSS update, for example after collection recreation. It does not model author assignment to `Animation.effect` or permit CSS to seize ownership of a script-replaced effect; that API override is a separate obligation. Full dispatch may still result in no collection, matching the native cancellation/empty-animation distinction. The model represents one selected effect field in a collection, not multi-animation matching or a collection-wide ownership bit. The reason is also externally supplied: equal-key verification ignores the supplied manager outcome, including cancellation. Actual cancellation must therefore enter through the authoritative full/null path before comparison; this module does not prove that routing or census of callers.

Thirteen declarations establish:

- Verification cannot create a missing collection; unknown samples dispatch; a skipped existing verification requires known equal input and preserves every modeled field.
- Full-update reasons dispatch even with equal input. Every admitted surviving update seeds the current key, without assuming a correctly seeded initial state.
- Cancellation erases collection history, and subsequent creation cannot inherit the old cache or script override.
- Retaining a script-owned effect preserves its override while updating the cache. Replacement does not carry that guarantee.
- A fresh cache does not certify that the manager applied base timing.

Six separately compiled false controls reject unknown-sample skipping, equal-key suppression of full updates, verify-only creation, preservation of an override across destruction/recreation, deriving applied base timing from cache freshness, and unconditional script preservation across replacement. They test distinct branches and interpretation boundaries; no native verification is inferred.

## Correspondence and remaining obligations

| Native seam | Model correspondence | Unproved obligation |
| --- | --- | --- |
| Existing CSS collection / empty snapshot | Outer `Option` / inner sample `Option` | Native typed duration lists are nonempty; empty array is a sound unknown sentinel. |
| Full reason versus verification reason | `dispatch` | Every required normal-restyle input change reaches this code; no dependency completeness claim. |
| Fresh base recascade at task execution | Operation's `key` | Actual element/pseudo, current input, and no script/flush interleaving. |
| Existing manager with composed UIReset | Independent `composedDuration` | CSS timing-source policy and conversion are not settled by this model. |
| Array swap then snapshot seed | Surviving `commit` | No failing/interleaved native operation separates these actions; collection remains valid. |
| Destroy/recreate collection | `commit` cancellation followed by full creation | Actual collection lifetime and target identity match this ownership boundary. |
| Reused animation's script-owned duration | `reusesEffect` plus `.script` | Native animation matching and existing override machinery preserve the same effect/field. |

The successful-commit theorem assumes a valid supplied key and successful modeled completion. The native null/display-none path cancels before comparison; allocation failure, partially executed manager work, exceptions, stale pointers and FFI ABI correctness are outside the model. There is no asynchronous callback, concurrency or reentrancy model. The synchronous source-contract argument remains separate from this kernel check.

Nothing proves parent/root freshness, late-parent publication, arbitrary-depth completion, convergence, cycle policy, same-query behavior, performance, a complete dependency key or native refinement. Snapshot equality may validly suppress a manager update while an already stale applied value remains; the cache is an admission key, not a freshness certificate.

## Actual check

Run1 compiled the unchanged import, this module, its thirteen axiom audits and six rejected false controls with pinned Lean 4.35.0-rc4. Actual session 4467, launch 5fbfd6, terminal d492a8/0. Audits use only `propext` or no axioms; no `sorryAx`, custom axiom or native reduction axiom is accepted. One harmless unused-simp-argument warning is retained in the log. Owned scratch was removed. No canonical theorem count is incremented.

Replay into a new artifact subdirectory:

```sh
python3 -I -S -B artifacts/css-contextual-duration-snapshot-lifecycle-model-v1/replay.py fresh-run
```
