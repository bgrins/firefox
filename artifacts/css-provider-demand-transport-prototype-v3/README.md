# Provider demand transport and cascade transaction prototype

Status: substantive three-file source prototype, uncompiled and not a complete provider fix. No live files, index, runtime epoch, browser, or native build were changed by this package. This supersedes the capture-only v2 archive, not the installed partial-v5 implementation.

Declaration substitution now distinguishes Invalid from Demand. Readiness-aware calls bypass cache hits, propagate Demand before parsing/cache insertion, and restore attribute-read tracking on Demand. Prioritary selection uses private shorthand-cache, attribute-tracker, revert-selection and deferred-declaration state; it commits only after all selected substitutions succeed. Inapplicable and reverted candidates are skipped using existing priority rules. Consumer seen bits, author flags, substitution cacheability effects and computed application occur after selection succeeds. Completed independent prerequisites may remain applied when a later consumer suspends.

Prioritary application distinguishes Applying, suspended ownership, and Ready. A checked constructor acquires consumer ownership; service-time reentry returns Demand. Only that continuation clears its suspension, including on Drop. Retrying rebuilds the private selection transaction while retaining the same borrowed Cascade, computed context, declarations, cache and attribute tracker. Existing callers use resume(None), so the ordinary path exercises new state ordering but does not activate the readiness scheduler. Acyclic Tarjan records now retire after application. Cyclic components retain their existing invalidation handling.

Default-plan construction consumes final cycle classification: Pending requests the provider, and InvalidatedParticipant forces Invalid regardless of a supplied CSS-wide reason. The plan borrows its exact registration. Inherited values are read from the current parent at computation, avoiding a stale early clone. Initial computation requires both completed prioritary prerequisites and a separate initial_context_ready certificate; that method defaults false. Unknown requirements remain unresolved.

## Remaining integration obligations

There is no readiness-Some caller, demand servicing loop, or complete initial-context discovery implementation. The borrowed application continuation is not itself a resumable Tarjan continuation. The next driver must keep the actual graph owner alive while servicing requests and must not turn scheduling-only dependencies into invalidating SCC edges or revive retired frames. A suspended call cannot simply return through the current traverse API and later pretend its DFS program counter survived.

Known prioritary bits are only scheduling requirements. Font metrics also depend on font-set generation and current/parent fonts; container lengths depend on per-axis ancestor sizing; viewport lengths depend on device dimensions; tree functions depend on element/scope/tree snapshots. Those computations publish dependency/cache effects. The initial_context_ready hook is a fail-closed contract, not a completed proof or collector. It must certify stable external context and effect publication in addition to bits. It must not become unconditional true or a syntax whitelist. Service callbacks must preserve target-context identity and legitimate completed prerequisites.

Staged forced-color adjustment reuses existing code. Current prioritary color-scheme adjustment does not take the color-alpha computation paths, but expansion of prioritary properties would require auditing effects in that helper. Rust panic recovery is not a supported retry path; Demand is the explicit suspension path. The legacy infallible wrapper cannot be used for a reentrant demand: the new driver must use the checked constructor/result API.

## Validation

Rustfmt with servo/rustfmt.toml parsed all three candidate files. Exact three-path patch check, apply, reverse-check, reverse, reapply and byte comparison run in owned scratch, which is removed. This is not typechecking or browser validation. Independent bounded source review is recorded separately; no native acceptance or formal coverage credit is claimed.
