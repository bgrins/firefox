# Finite DAG completion with incremental rule edits

This isolated Lean model generalizes the earlier Boolean copy chain to a finite directed acyclic dependency graph with arbitrary deterministic, total value functions. It proves preservation of dirty-work coverage, consistency at quiescence, bounded completion under full snapshot rounds, and uniqueness of the consistent value assignment. Incremental admission is derived from an explicit rule edit; post-edit coverage is not assumed.

## Concrete algorithm and assumptions

`Graph n V` contains `Fin n` nodes. Each node has an ordered finite dependency list, a pure function from the corresponding `List V` to its value, and a natural-number rank. Every listed dependency has strictly smaller rank. Dependency lists may share nodes, contain several inputs or repeated inputs, and need not be in rank order. The node function can distinguish the order and multiplicity of inputs. Value equality is decidable for the executing algorithm.

A state contains current values and dirty flags. A full `round` evaluates every dirty node using only the pre-round dependency values; clean nodes keep their values. It retires the old batch and marks a node dirty exactly when any listed dependency changed value during that batch. This is a concrete notification rule over changed inputs, not a check that simply queues every currently inconsistent node. Evaluation is explicit in `values`; retiring work is not itself evaluation.

`Covered` means every node inconsistent with its current dependency values is dirty. It allows redundant dirty work. `Ready` means all nodes in this finite graph are clean; `Consistent` means every value equals its node function applied to its current dependency values. A ready state alone is insufficient, as `discarded` demonstrates.

The graph, rules and external inputs are fixed throughout each `run`. External input changes are represented by changing zero-dependency constant rules before the run. The model does not accept impure rules, mutable hidden inputs, topology edits, reentrant edits during evaluation, or queue changes outside the specified algorithm. An application must identify a dependency-closed set of relevant nodes; the separate unrelated flag is not an excuse to omit actual dependencies.

## Derived results

- `round_covered` preserves coverage from any covered input state. If a node is not requeued, all its listed dependency values stayed equal. A dirty node was evaluated against those values; a previously clean node was already consistent by the incoming invariant.
- `ready_consistent` then establishes local value consistency. `consistent_unique` uses decreasing ranks to show that two consistent states of the same graph have identical values.
- `round_frontier` proves that if dirty ranks are at least k, next-round dirty ranks are at least k + 1. A new notification requires a changed dependency, and a changed dependency must have been dirty and have lower rank.
- `bounded_completion` gives readiness and consistency after `height + 1` full rounds for a covered state when every rank is at most `height`. `arbitrary_initial_completion` supplies covered admission by queuing every node, regardless of its initial value. Ready states stay ready and their values remain unchanged.
- `edit` replaces only the rule functions on an explicit finite edited-node list; dependency lists and ranks are retained. `admit` preserves values and queues exactly those edited nodes. `edit_admission_covered` derives coverage from prior consistency: an unedited node has unchanged rule and inputs. `incremental_completion` then applies the general bound. Because admission replaces the dirty set, this theorem requires prior settled values; it does not authorize replacing outstanding work during an unsettled computation.

The bound is for synchronous full-batch rounds, with no scheduler fairness abstraction. It is not a bound on Gecko traversals, a recommendation for a fixed number of passes, or a claim that a native traversal evaluates one dependency layer. A topological evaluator may finish sooner; arbitrary fixed round budgets do not uniformly cover unbounded graph height, as the existing chain model already proves.

## Multiple-input examples and rejected controls

The four-node diamond has a constant root x = 2, branches a = 3x and b = x + 1, and shared dependent z = a + b. Starting from all-zero values with all nodes dirty yields:

| Completed snapshot rounds | x | a | b | z |
| --- | --- | --- | --- | --- |
| 1 | 2 | 0 | 1 | 0 |
| 2 | 2 | 6 | 3 | 1 |
| 3 | 2 | 6 | 3 | 9 |

After round 2 only z is dirty; its stored value is 1 while its current inputs require 9. The consistent final solution is unique.

An incremental constant-root edit from 2 to 4 queues only the root and evolves from the settled old state through `[4, 6, 3, 9]`, `[4, 12, 5, 9]`, and `[4, 12, 5, 17]`. Omitting admission leaves the old state quiescent and inconsistent. A separate edit changes only the second branch from 3 to 8. The real notifier queues z and produces 14; the deliberately broken `firstDependencyOnly` notifier ignores that second input and loses coverage while appearing ready. An unrelated pending Boolean remains true alongside a ready, consistent diamond; no global drain obligation is claimed.

Six compiled false controls reject: empty queue alone implies consistency; two rounds complete the initial diamond; rule edits need no admission; one round evaluates the whole incremental diamond; watching only the first dependency preserves coverage; and the second input does not matter.

## Checked evidence and scope

Final actual run: launch `bac5c4`, session `84231`, terminal `71c538/0`. `run6` records 23 named axiom audits, six semantic false-control rejections, exact final source hash, pinned Lean 4.35.0-rc4, and removed scratch. Only standard Lean axioms occur; no `sorryAx` or native-reduction axiom is admitted. Earlier source snapshots/logs retain development diagnostics in runs 1–5; their temporary directories were removed. No compiled Lean artifacts are retained.

Reproduce into a fresh, absent output directory:

```sh
python3 -I -B -S artifacts/css-contextual-duration-dag-completion-model-v1/replay.py replay-independent
```

The earlier Completion model separately represents queued/in-flight work and proves an exact chain frontier. This module instead makes whole-round evaluation atomic and proves a general fan-in invariant for arbitrary values and rule updates. It does not import or modify that model or QueueState and does not prove that a native queue entry maps to its dirty flag. The existing cycle model remains a counterexample to extending acyclic fixed-input completion to feedback; no CSS cycle policy is selected here.

No CSS numerical oracle, native scheduler/refinement theorem, browser observation, same-query repair, new accepted bug, or canonical Lean coverage increment is claimed. Mapping native property dependencies, actual evaluation, complete invalidation, query closure, in-flight work and reentrant mutations to this algorithm remains an external obligation. The full-round assumption must not be inferred from posting, removal or preparation markers in a trace.
