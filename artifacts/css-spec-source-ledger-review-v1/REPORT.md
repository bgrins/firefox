# Independent Fragmentation source-ledger review

## Result

**Accept the pilot's fragmentation source accounting as lexical accounting, with interpretation still proposed.** The independently derived interpretation is in INTERPRETATION.md, with thirteen concrete requirement candidates and eight distinguishing scenarios. They are useful inputs to Lean contract review, not accepted formal semantics or coverage of all fragmentation.

I read the primary ED and published CR before reading the producer importer or interpretation frontier. The only producer material read initially was the source lock, to agree on exact bytes. Root confirmed the ED profile. The independently written requirement inventory predates the importer review; ACCOUNTING.json records its hash.

## Accounting checked

The pinned ED has 274435 bytes. The independently selected section is byte interval [99200,104879), from the Unforced Breaks heading through content before the next peer heading, best-breaks. It exactly equals the importer's selection. Its 174 lexical units include the entire introductory paragraph, four rule bodies, and four later fallback paragraphs: five p starts, four dt starts and four dd starts. The nested monolithic-breaking span does not truncate the progress text. There is no table inside this section.

Concatenating the raw byte slices of all whole-document units reconstructs the exact original source. UTF-8 byte offsets and hashes are source-bound. This establishes no missing bytes for this snapshot; it does not classify those bytes into exhaustive normative requirements. Rule headings, nested links, prose and whitespace being independently counted is lexical structure, not thirteen or 174 semantic obligations.

I read the complete importer and checker. validate checks source binding, ordered byte partition, per-unit hashes and deterministic IDs. The full checker regenerates lexical inventories before comparing them with retained output. These checks have different jobs: validate alone does not recompute category labels, candidate bounds or reference maps. Claims must keep that distinction. HTMLParser event streams are not a browser DOM or a normative grammar parser.

The importer calls semantic categories and selected context candidates, and the interpretation frontier explicitly retains unresolved human dependencies. Those qualifications are necessary. The href-only reference frontier cannot find unlinked adjacent requirements, implicit external concepts, figure content behind src, or semantic contradictions between a link and its visible text. Whole-document bytes remain accounted for, but dependency closure is not established.

## Specific omission and profile risks

- All four fallback paragraphs are essential; a four-rule inventory alone is incomplete.
- The adjacent zero-size placement obligation is outside the selected range. It is correctly retained manually through best-breaks, not claimed automatically extracted.
- The §4 minimum-size premise and §§4.1–4.3 opportunity/forced-break rules remain external dependencies.
- The section itself contains no table, but break-control property tables and line-count validity are external normative inputs.
- Rule 4's class B label links to class A. The retained source includes both. The proposed B/C interpretation needs explicit expert disposition; anchor existence does not resolve it.
- Published CR and selected ED differ at the second decoration truncation stage. Both source identities are retained here; no merged interpretation is implied.
- Class/type-specific avoidance needs a reviewed applicable-value normalization interface. Literal Rule 2/4 wording must not silently become an implementation's guessed normalization for avoid-page/column/region.
- Normative prohibition, permission, optional weighting and progress must remain separate requirement kinds. Optimal-looking page output is not a universal exact oracle.

## Next concrete implementation

Review and bind the thirteen candidates to the nine source content units, allowing several candidates per unit. Resolve the Rule 4 label/link discrepancy and applicable-value normalization. Add dependency records for best-breaks and the opportunity/geometry providers before asserting any semantic closure.

Then implement a finite supplied-opportunity relation with stage-specific necessary constraints, independently justified geometric insufficiency, and admitted choices. Prove selector soundness and existence on a nonempty input domain. Use the eight scenarios as counterexample obligations rather than a substitute for the universal theorem. A finite cursor measure can prove termination for the pilot; positive progress over arbitrary real geometry cannot alone prove termination.

No native implementation, browser behavior, all-document semantic inventory, or completed Lean theorem is claimed by this review. The importer remains an implementable source-accounting tool with an explicit human interpretation frontier.

## Recheck

Run `python3 -I -S check.py`. It checks the retained source identities and independent section boundary/count evidence, then verifies the compact artifact roster. The producer source/ledger hashes in ACCOUNTING.json identify the inspected checkpoint, not an assertion that later producer edits were reviewed. No elaborate capsule or native build is required.
