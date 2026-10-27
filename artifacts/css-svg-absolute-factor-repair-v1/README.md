# SVG absolute-unit factor repair proposal

Correct three literals in `SVGLength::GetAbsUnitsPerAbsUnit`: inches per Q5/508, picas per Q15/254, and Q per inch508/5. Keep the table shape, indexing, predicates and other46 literals unchanged. The standalone patch contains exactly SVGLength.cpp and two WPT files, with16 main cases. This is a proposal for isolated comparison, not an accepted or installed fix.

CSS Values4 section6.2 defines the exact absolute-length ratios: https://drafts.csswg.org/css-values-4/#absolute-lengths. The native candidate’s three replacements are decimal float approximations of those ratios. The original table was byte-identical on HEAD90, retained upstream976 and the observed working tree. These coefficient errors are independent of the installed114 context-readiness repair; no DOMSVGLength source is changed here.

## Observed regression scope

The12-case DOM conversion diagnostic on the accepted114 working tree has6PASS/6FAIL. Detached/scalar/list Q→in and Q→pc fail at the converted-factor assertion after source parsing, independent pixel value and destination-unit calibration. Q→px/mm controls pass. The landing file removes only the unused rows array, rows.push and global observation export; all names and assertions are retained. Failed diagnostic cases do not establish later repeat/pixel-preservation assertions.

The separate four-case SMIL diagnostic has2PASS/2FAIL on the same source/binary epoch. Length-list interpolation from1in→0q at3s and0q→1in at1s observes10.713623046875px instead24px. The other two samples pass at72px. Static inch/Q, viewport, paused timeline, initial/reference values, rewind and endpoint assertions precede the failing interpolation assertion. Later repeat assertions on the failing cases are NOT_REACHED. Source inspection explains that interpolation can select Q as the destination without going through public convertToSpecifiedUnits target validation; zero-Q endpoints neutralize the separate Q→in error. This is observed public animation behavior plus source attribution, not a native branch trace. The final SMIL fixture is byte-identical to the observed diagnostic, with only its installation pathname changing to `svg/animations/SVGLength-quarter-millimeter-interpolation.html`.

Both runtime capsules and their raw/root preservation receipts are pinned in REFERENCES.json. Neither source epoch is described as pristine upstream. The planned comparison must normalize to HEAD90 and apply only this factor candidate to establish independence from pending repairs.

## Static and compiled checks

The candidate extracted helper passes all49 independent rational-double comparisons under UBSan+integer, all65536 unit-predicate inputs and15 NUMBER alias checks. There is no sanitizer output. The tolerance and original three discrepancies are justified in the preceding helper audit; it is not a normative CSS accuracy threshold. The copied harness retains the original class shell, predicate, oracle and compiler settings; only the exact candidate function and nested harness root path differ. Full Gecko build/browser candidate results remain pending.

The complete three-path patch applies and reverses exactly in owned scratch copies of both HEAD90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e and upstream976279105b2e78b8666a959eb3f25c9176cefaf8. All three resulting bodies match PATHS.json; reversal restores the original source and removes both new tests. Scratch directories and compiled products were removed. These textual checks do not establish clean-upstream runtime behavior. Changed-line clang-format produces no delta; both fixture scripts parse. WPT lint is deferred to the guarded comparison.

Exact-path Herald lookup identifies `#firefox-svg-reviewers`. No commit, staging, native installation, new accepted number or parent revision is assigned. Discovery came from source/numeric inspection; the extracted C++ check and browser diagnostics confirm it without a Lean-discovery claim. Accepted central111 and all installed SVGLength114 tests remain separate.
