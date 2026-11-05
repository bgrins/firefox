# Incremental candidate: bounded occurrence trace

Prepared only. `native.patch` and `candidate/servo/components/style/properties/cascade.rs` overlay exact incremental source `d32913bd213ebaf1e5bbff4ed7117ec8af0003990807f6a3f2c3f5ed7ded41f1`. The old diagnostic and incremental candidates remain unchanged. No live source, Git index, build or browser was modified or run.

The existing `DeclarationSources::trace_occurrences` hook is moved into its own implementation block, then called from `RuleExclusions::new` before the new incremental cursor is created. It reads the complete source roster under existing guards, without consuming that cursor. Enable with environment `CSS_OCCURRENCE_TRACE=1`. The gate uses presence, matching the old hook; a value of `0` also enables it.

Caps remain 128 first-Rule calls per process, 64 rule-tree nodes per call and eight declarations per source. Beyond the cap the diagnostic stops logging, not cascading. Source-less nodes count toward the node bound. Direct-block calls are labeled separately. The new log-only fields are explicit importance, per-source declaration counts, and final source/entry totals. These avoid decoding importance from packed Debug values and let the checker reject dropped records. Raw and normalized priorities still include their complete Debug representations, including flags. No logged pointer is dereferenced outside its borrowed lifetime.

This trace walks sources eagerly and logs synchronously. **Use a separate diagnostic build/run, never performance measurements.** The code was rustfmt-formatted and the patch verified forward/reverse on temporary copies; it has not been typechecked or built here. `SOURCE.json` pins the preimage and prior diagnostic. `CHECK.json` retains preparation commands and results.

## Analyze retained records

```sh
python3 -B artifacts/css-revert-rule-incremental-occurrence-diagnostic-v1/analyze.py \
  path/to/raw.jsonl --output artifacts/NEW-occurrence-analysis.json
```

The input is retained WPT JSONL, not scraped console output. Only `process_output.data` records are considered. The checker never modifies the input or overwrites an existing report. Its report pins the input SHA256 and counts parsed records. `event_index` means zero-based parsed nonempty JSON records, with source/entry event indices retained in each witness. Multiple lines within one data record are accepted. Embedded or malformed marker wrappers are reported rather than guessed.

Native calls are grouped by their **embedded content PID and call counter**, never the WPT record's `pid` (harness PID) or `process` (launched-browser transport). No pointer comparison crosses calls, PIDs or input files. Root must supply a single retained process-lifecycle run; this format does not carry a process-generation identifier for hypothetical PID reuse.

A complete roster requires one final end record, matching source and entry totals, all declaration entries claimed by each source, ordered distinct source ordinals, consistent entries for repeated block pointers, and no relevant node/entry cap. Duplicate/out-of-order records, missing entries/end and inconsistent addresses invalidate that call's witnesses. A later global call-cap is reported by PID; it limits subsequent observation but does not erase a completed earlier roster. No-count legacy traces intentionally fail this checker.

For a complete roster, `same_raw_priority_nonadjacent_pairs` requires:

1. The same retained block pointer and matching original declaration pointers/property IDs.
2. Equal **raw full** priority text, equal normalization and equal importance.
3. At least one intervening source with a different block pointer.

Each pair retains the intervening source and original-entry details for review. Results classify ordinary and important pairs separately. Adjacent repeated copies are reported separately. `ordinary_important_pairs` requires opposite importance and equal normalized priority but different raw priority; this is the normal/important counterpart expected from a single source occurrence, **not evidence of two semantic rule occurrences**.

Matching pointer rosters establish allocation sharing within that invocation. They do not prove declarations were evaluated, excluded or responsible for an observed value, nor that the intervening source supplied the winning property. Review the retained declaration IDs and fixture structure for those narrower joins. No actual native observation is supplied by this package.

## Phase attribution and controls

Existing `CSS_OCCURRENCE_PHASE_V1` markers identify family, direction, side and setup/read intervals. The checker retains those as `candidate_phase_contexts` using their transport stream. The JS markers lack a content PID and element identity, so this is explicitly **transport-interval context**, not a certified element/cascade join. A roster spanning intervals retains all candidate contexts without discarding otherwise valid within-roster pointer evidence. Unmatched phase boundaries are reported as input-integrity issues. Asynchronous initial-style work can fall outside read markers.

The independently parsed fixtures use distinct URLs/comments within each roster. A stylesheet may still be cached across different test iframes; that does not invalidate within-roster independence and must not be diagnosed by comparing pointers between calls. Loading the same URL successfully is not proof of sharing. Require a positive same-raw-priority roster witness for the intended shared case, and inspect the corresponding control's complete source roster. An absent witness can mean no sharing, prior deduplication, a skipped first-Rule path, an incomplete trace or missing attribution; it is not a semantic counterexample.

`input_integrity_ok` describes retained records only. It does not mean all browser cascades were observed, a WPT passed, or the implementation is correct. `native_observation_present`, call caps and per-call completeness must be inspected separately. CLI exit 0 means record integrity passed; it can still contain zero native calls or zero sharing witnesses.

`check_parser.py` exercises synthetic positive and negative controls, including same-phase/cross-phase distinctions, flags, missing records, caps, PID/call isolation and weak phase binding. These are parser tests, never native measurements. Run it with `python3 -B` to avoid persistent bytecode directories.
