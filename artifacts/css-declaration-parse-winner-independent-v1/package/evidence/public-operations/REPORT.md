# Declaration block public-operation audit

## Disposition

No new reachable browser defect established. The inspected push, extend, remove and clear bodies preserve the three storage invariants under valid initial state and normal completion. The strongest useful next proof is arbitrary operation-sequence preservation with an explicit fresh-removal certificate, followed by caller admission. This report supplies source contracts; it does not duplicate the ordinary-update producer or claim native universal verification.

All work was read-only except this artifact directory. No native compilation, browser execution, production/WPT change or Git operation occurred. Searchfox identifier discovery succeeded initially; later attempts to save its output failed DNS and those failures are retained. PUSH-CALLERS.json independently records the current local sites after exact discovery. Full snapshots and hashes are retained. Layout instructions and review docs were read using Python because no Read tool is exposed.

## Storage relation and constructors

Let D be the ordered declaration vector, I the ordered importance vector, and S the property-ID membership set. Require (1) length D = length I; (2) IDs in D are unique; (3) S is exactly the set of IDs in D. IDs distinguish custom names from longhand tags, and CSS-wide/WithVariables declarations retain the underlying property ID. Payload comparison is unnecessary for these four operations.

`new` establishes empty D/I/S. `with_one` inserts exactly the supplied declaration ID, one payload and one importance. `clone` copies all three and clears the immutable flag. `clear` empties all three and does not reset immutable. Shared-memory cloning copies all three and marks immutable. Heap/refcount/threading and immutable-call admission remain external.

`from_animation_value_map` is another constructor: it inserts each map key into S but pushes `animation_value.uncompute()` into D. Map-key uniqueness alone is insufficient; the necessary provider premise is key == uncomputed declaration ID. No mismatch or reachable defect was found, and this audit does not prove every AnimationValueMap producer. Keep this admission explicit in any theorem covering arbitrary constructors.

## push: parser priority and order

`push` first inserts the ID into S. For an existing ID, valid membership plus uniqueness gives exactly one matching vector slot. Existing important plus incoming normal returns false without changing D/I/S. Otherwise it removes the matching D and I entries and appends the incoming declaration and its importance. For a new ID it appends both. Therefore accepted replacements move to their last-winning source position, and skipped lower-priority declarations retain their old position.

The result is false only for that priority rejection; true does not mean unequal payload or changed serialization. Identical accepted values still move to the end and return true. This matches declaration-list parsing, not the CSSOM setter algorithm. Reusing push to implement setProperty would incorrectly preserve old important declarations when the setter requests normal priority. Existing style-cssText-mutations.html explicitly checks that CSSOM lowers priority.

The general source reference is: for each ID keep the last important occurrence if any exists, otherwise the last occurrence, then retain those winners in source order. For extending a nonempty block, treat its unique entries with their existing importance as the initial source prefix. This reference does not assume reflexive payload equality.

## extend: sequential parser fold

`extend` reserves an upper bound from ordinary drained declarations plus the expanded all count, then pushes all ordinary declarations in order, followed by all expansion. The changed result accumulates with non-short-circuit bitwise OR in both loops. Every push executes even after true. Input duplicate IDs and mixed logical mappings are structurally safe here: sequential push deduplicates them. This differs materially from precomputed ordinary update plans.

The iterator itself determines exact expansion order and all exclusions. A theorem may parameterize its finite ID/payload stream, but a native/caller bridge must bind AllShorthand::declarations and metadata separately. Reserve arithmetic, finite lengths, allocations, ArrayVec drain behavior and normal completion remain admitted; this report does not prove failure atomicity.

## remove_property: earliest current index is essential

`first_declaration_to_remove` uses membership as an early return for a longhand/custom property, then searches for the first ID matching the target or its shorthand expansion. `remove_declaration_at` removes the ID from S and removes the same index from I and D. `remove_property` first removes the supplied index. For a longhand/custom target uniqueness makes that sufficient. For a shorthand, it scans the remaining suffix, keeping the index unchanged on removal and advancing only on retention; the length decreases with each removal. Because the supplied index was earliest, no earlier matching declaration can survive. The result is exactly stable filtering of all targeted IDs.

The debug assertions check this certificate but release behavior trusts it. A later matching index is not enough. For example D=[margin-top,color,margin-left] with a supplied margin index 2 leaves margin-top; D=[color,width] with cached width index 1 followed by removing color makes that cached index out of bounds. These are API-premise counterexamples, not executions or browser bugs. A structurally invalid starting block with duplicate color IDs also demonstrates why removing only one longhand could desynchronize S from D. The prior accepted duplicate-publication repair addresses a concrete historical producer; no current path was found here.

## clear and actual callers

`clear` unconditionally clears I, D and S. The only discovered Rust external entry is Servo_DeclarationBlock_Clear. Its two C++ consumers are MappedDeclarationsBuilder's constructor and SVG MappedAttrParser's constructor, which clear reused presentation-attribute storage before rebuilding. CSSOM cssText replacement uses fresh parsing/SetCSSDeclaration rather than this in-place clear entry, so lack of a callback in Clear is not by itself a missing CSSOM mutation notification.

### Caller ledger

| Operation | Actual discovered callers | Admission or disposition |
|---|---|---|
| extend | PropertyDeclarationParserState::parse_value; glue parse_property | Parsed declaration lists drain only after importance and exhaustion succeed; standalone parse creates a new block and uses normal priority. Error handling clears scratch. |
| push | extend's two loops; 22 glue sites | See PUSH-CALLERS.json. Internal value setters push normal declarations; canvas adds three normal overrides; computed/typed serialization builds fresh blocks. |
| remove_property | glue remove_property, reached by two exported RemoveProperty functions | Earliest index computed under read lock, callback invoked, then current block mutably locked. Stability across that seam is required. |
| clear | Servo_DeclarationBlock_Clear | Reused mapped-attribute storage, not direct CSSOM clear. |

The internal setters include identifier, integer, MathDepth, list-item counter reset/set, pixel/path/percentage/auto/currentColor/color/font-family/background-image/text-decoration/aspect-ratio. They are internal typed interfaces, not the string CSSOM setter. Arbitrary valid initial priority still preserves storage even if an intended force-override semantic would require a separate caller contract. Every downstream C++ typed-setter consumer has not been exhaustively audited here.

Canvas initially looked like a force-override misuse: important line-height would survive normal push. Its only discovered SanitizeForCanvas caller is CreateDeclarationForServo after ServoCSSParser::ParseProperty for the font shorthand. The Rust standalone parse extends a new block with normal importance and does not parse !important. Thus the suspected important blocker is not admitted by that caller. No canvas bug proposal follows.

## Removal callback and stale-index admission

The Rust helper releases the read guard before the callback and reacquires a write guard afterward. Its FFI callback can theoretically mutate anything; the type alone does not guarantee index stability.

The actual CSSOM path computes the old returned property value, creates mozAutoDocUpdate, ensures a mutable block, then calls RemovePropertyById and publishes only when it returns true. mozAutoDocUpdate either calls Document::BeginUpdate (which adds a script blocker) or adds a script blocker directly. The concrete inline callback is MutationClosureFunction: it does activity bookkeeping, marks its once-only closure data, then calls InlineStyleDeclarationWillChange. The latter asserts script is blocked and notifies native mutation observers. nsMutationReceiver::AttributeWillChange records target/name/old value rather than invoking the author MutationObserver callback. This rules out the straightforward synchronous author-JavaScript reentrancy hypothesis.

Native ancestor observers and PresShell still receive synchronous callbacks; no complete proof of every observer's nonmutation, activity hook, lock lifetime or thread discipline is claimed. The formal boundary should be preservation of the selected target block's ordered IDs across the callback (or a stronger complete-block stability assumption), not a globally empty event trace. Mutation records can be queued while this property holds. The ordinary update model needs the stronger plan-relevant stability relation owned by its producer.

## Normative and test oracles

Current primary CSSOM and Cascade drafts were consulted. SPEC-TRACE.md gives the precise distinctions. Existing retained WPTs cover parsing important precedence, priority lowering by setProperty, indexed removal, shorthand/all removal, absent-target no-mutation, and style-attribute old-value records. They were read, not run. No new failing WPT is justified by this audit.

## Recommended universal contracts

1. Define valid storage as unique D IDs, exact S membership and aligned I; prove new/with_one/clone/clear preservation.
2. Prove push equals the priority-aware winner/reference rule, including unchanged rejection and append order. Prove preservation with arbitrary payloads and no payload equality premise.
3. Lift push to arbitrary finite extend streams, exact concatenation order and accumulated change flag. Do not import ordinary-batch source uniqueness/mapping restrictions unnecessarily.
4. Define a removal certificate from the current D and target predicate. Prove first-search soundness/completeness, stable-filter removal and aligned membership/importance. Carry the certificate through a callback with an explicit frame condition.
5. Induct over arbitrary legal operation sequences, with removal certificates refreshed at each removal and constructor provider premises maintained. This is not arbitrary calls with arbitrary indices.
6. Admit native widths, reserve arithmetic, container operations, normal completion, generated property identity and mutable-block lifetime separately. Compose ordinary update only once its independently owned proof and source admission are available.

These contracts reduce the real public-operation scope without weakening its original source/caller obligations. No performance claim or new accepted bug is requested.
