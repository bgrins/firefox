# Writing-mode scheduling proposal v2

Isolated two-Rust-file, three-WPT-page candidate against signed committed HEAD `6eb538c23bcf3dde9c7631a1c826cba4de562462`. Exact HEAD native bodies equal the v1 original captures. No held admission or zoom overlay is a source prerequisite. Compilation, real WPT execution, upstream transport and genuine cycle policy remain outstanding; this is not an accepted or independently validated landable fix.

The native delta from v1 restores the entire original LineHeight prerequisite block: LhUnits visits only FontUnits in the SCC graph. It no longer visits WritingMode merely because the implementation normally applies WritingMode first. Existing `ensure_prioritary_property` application ordering and `PrioritaryPropertyId::dependencies()` remain byte-identical to HEAD; the LineHeight dependency list in `properties/data.py` still includes WritingMode. This removes the confirmed synthetic SCC while retaining ordinary computation ordering.

Actual selected logical-unit references still request the new WritingMode node after substitution and registered grammar admission. WritingMode declarations retain selected provider/attribute backedges. Invalid values and unused logical-unit fallbacks remove only the new contextual bit. Existing font/line-height/color behavior stays unchanged. Preparation/cache mechanics are directly included in this patch, not supplied by held A. All v1 supported registration syntax, logical viewport units and cqi/cqb classification remain; no syntax was excluded to evade controls.

The exact 16 acyclic logical-unit tests and four selected-fallback/invalid-grammar tests are unchanged. New `registered-writing-mode-fixed-line-height.html` adds eight tests varying parent writing mode, declaration order and query order. Each captures all 40→60→40px line-height states before assertions. A sibling substitutes a literal registered length into writing-mode to calibrate grammar rejection and inheritance. The contextual sibling must retain the current fixed line-height as its registered value; writing-mode inherits in both. No disputed genuine-cycle oracle or style-query support is required. Browser callbacks have not run.

## Remaining application boundary

Removing the SCC edge does not make `ensure_prioritary_property` a readiness evaluator. It marks a property ensured, recursively applies broad implementation prerequisites, then applies the property. LineHeight can therefore request a variable-bearing WritingMode while a provider remains open. For the fixed-lh witness the consumed length cannot satisfy writing-mode's grammar, so inherited defaulting is correct. This does not establish safety for if()/style() branches that can produce valid keywords.

A general follow-up must separate settling providers actually read by the winning selected declaration from scheduling context prerequisites needed by its admitted value. Open providers require an explicit incomplete result before inserting `ensured_prioritary` or publishing a value from a provisional map. Broad `id.dependencies()` cannot simply become Tarjan edges; skipping needed prerequisites is also incorrect. This candidate does not change that API or settle genuine vi/if cycle-defaulting.

The genuine `--n:100vi; writing-mode:var(--n)` and valid if()/style() reciprocal-dependency examples remain observations. The retained actual WM edge feeds existing SCC invalidation as an experimental choice, not as a claim that published specifications settle every such cycle. The fixed-lh false-cycle control is normative and separate.

## Validation

Fresh Searchfox discovery 8a33e1/0 located generated dependency definitions; ReferenceFlags query 28f96b/0 identified no additional external storage consumer in its bounded indexed result. This is not a complete ABI audit. Exact local HEAD captures are the editing bases.

Rustfmt edition2024 passed cf9c37/0. Five-path patch forward/reverse/reapply at fuzz zero, JavaScript syntax and 28 unique test registrations passed 2bcf8d/0 in an owned temporary directory which was removed. No callbacks executed. No native sources, live WPT, index, HEAD, epoch, browser, build, acceptance count or canonical Lean coverage changed.
