# Bounded writing-mode v3 review

Verdict: suitable for a controlled original/candidate experiment, not acceptance. The two native files are an original-HEAD proposal, with preparation included locally rather than supplied by held admission/zoom overlays. No native compilation or browser run was performed in this review. All referenced package payload hashes were authenticated.

## What the source establishes

`find_non_custom_references` admits the new WRITING_MODE bit for every non-universal registration, independently of the old LENGTH descriptor mask. This avoids excluding numeric division or syntax alternatives merely because their result is not a length. `from_unit` covers cqi/cqb and all eight logical viewport variants. It does not expand cqmin/cqmax policy. The four-entry NonCustomReferenceMap matches its four enum variants.

`visit_value_references` retains the existing selected-primary/fallback graph walk and additionally checks whether each visited primary remains on the component stack. Preparation is conditional on all such providers being settled, a non-universal registration, and a carried WM bit. It substitutes once, parses against the actual registration, retains the admitted specified value and taint, and removes only WM when the result is invalid, CSS-wide, or the selected token scan lacks that unit. An unsuccessful scan preserves WM. Existing font/LH/color flags are not generally refined. The owned value is computed only after its SCC is popped without a cycle; a cyclic component cannot publish the cached value. CSS-wide application was factored from the existing path; invalid values still use existing registered defaulting. This is a bounded code review, not a general proof that early parsing is effect-free for every supported grammar.

V3's singleton declaration precedes composites. The existing actual-bitflags 512-mask probe and separate kernel-checked model address that iteration defect; they do not validate this cascade scheduling. A bounded fresh Searchfox ReferenceFlags identifier search returned 52 hits in the two relevant Rust files, with no additional storage consumer exposed. This is not an ABI/ToShmem proof or a substitute for compilation.

## Concrete readiness gap beyond genuine cycles

`ensure_prioritary_property` marks a property ensured before recursively applying its implementation prerequisites. LineHeight still includes WritingMode as an application prerequisite, although the synthetic LH-to-WM SCC edge was correctly removed. Therefore a mixed lh/logical registered value can apply WM before the WM graph node has visited/admitted WM's registered providers. `substitute_one_reference` recursively substitutes a still-universal provider as tokens; it does not perform that provider's registered grammar admission/defaulting. The subsequent WM-node visit cannot reapply a property already marked ensured.

A concrete acyclic probe, with inherited horizontal-tb and fixed line-height 40px:

```css
/* --wm registered as <length> | horizontal-tb | vertical-rl, initial vertical-rl;
   --n registered as <length>, initial 7px. */
--ready: bogus;
--wm: var(--ready, 1vi);
writing-mode: var(--wm);
--n: calc(1lh + 100vi);
width: var(--n);
```

If --n is traversed first, its FONT/LH bits are visited before WM. Ensuring LH can recursively substitute the still-unadmitted --wm to `bogus`; WM then inherits horizontal-tb. Later --wm admits as invalid and defaults to vertical-rl, but WM is already ensured. If --wm settles first, its registered initial keyword is available. The logical-unit token occurs only in an unused fallback, so this does not depend on disputed genuine vi cycles. The proposal's source permits this premature application; actual branch iteration/outcomes have not been observed. It can overlap an existing baseline scheduling limitation and is not a newly counted bug or proven candidate regression.

This should be a targeted acceptance check even if all 36 prepared tests pass. Vary property names and declaration/query order because `seen.var` iteration does not promise declaration order. Compare direct literal vertical-rl, a registered literal vertical-rl provider, the invalid selected primary above, and a used fallback yielding vertical-rl. Record all provider/custom/WM/width values before assertions. A real fix must settle/read the selected provider before publishing WM, or return an explicit incomplete result; merely reinstating LH-to-WM as an unconditional SCC edge revives the fixed-lh false cycle.

## Smallest useful experiment

1. Authenticate original native bodies against the captured source roles and use a clean committed-native baseline. Build original and the exact two-file candidate separately, with the same four isolated WPT pages (36 identities): 16 logical-axis mutations, 4 selected-fallback/invalid-grammar controls, 8 fixed-lh controls, 8 mixed-unit controls. Prior 16-failure evidence used the admission-only binary, so retain that historical provenance rather than call it this original phase.
2. Add the acyclic provider-readiness probe as a separate diagnostic supplement before acceptance, retaining every snapshot and original/candidate outcome. Do not replace or weaken the 36 existing identities. Small/large/dynamic viewport aliases, root contexts and typed-attribute inputs are additional coverage gaps, not established defects.
3. Preserve the existing font/LH/attribute/cycle regression roster and full unresolved failure messages. Keep genuine vi/if()/style() cycles observation-only under the existing policy trace. A pass on the fixed-lh tests checks removal of the synthetic SCC; it does not settle all actual-read cycle policy.
4. Compile both native configurations and check u16 flag/derived storage integration. Only then assess exact failures and whether this can be a standalone fix+WPT commit. No accepted-count or canonical Lean coverage change is justified by this review.

Read evidence: native diff feab84/0; scheduling/visitor reads b34732/0,7e07b0/0,6b378d/0; recursive substitution cd4abb/0. Fresh Searchfox dependency lookup39cdf5/0, full data.py retrieval095fa3/0; an unsupported line-range CLI attempt e5ade4/2 was corrected. ReferenceFlags lookup d7c1e7/0. These indexed lookups corroborate the dependency shape; captured candidate files, not moving indexed source, are the exact review subjects.
