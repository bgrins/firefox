# Visible table fragmentation calibration proposal

UNEXECUTED_CALIBRATION. The original sealed 20-case provider fixture remains unchanged. Parent observed all eight fragmented cases fail visible cell geometry before candidate phases; these are eight calibration failures, not eight hidden-query defects or candidate regressions.

## Source obstacle

Searchfox discovery resolves mTableIsSplittable to nsColumnSetFrame, nsPageFrame, nsTableFrame and nsTableRowGroupFrame. Local HEAD90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e and working bytes are equal for ColumnSet, Table and RowGroup (LOCAL-SOURCE-BINDINGS). The multicol caller explicitly sets mTableIsSplittable=false. RowGroup::Reflow requires that flag before SplitRowGroup. Table additionally combines pagination and constrained size with the flag. Indexed complete source/logs and actual local snippets are retained. This source path explains why assuming a real table continuation in screen multicol is unsafe; it is not a full runtime flag trace.

Changing empty content to a solid nonempty child or adding break-before:column does not remove the source flag gate. No promise those variants will split. Paginated continuation testing is a separate route; a page test is not interchangeable with this screen CSSOM fixture.

## Spec and existing tests

Retained webspec-index CSS-BREAK-3 possible-breaks says sibling table rows/row groups supply class-A break opportunities. break-between describes break-before/after controls. Existing WPT css/css-break/table/break-avoidance-001.html uses table cells in multicol; break-before-expansion-001.html explicitly requests a column break on a cell. Their existence does not establish current Gecko support or passing metadata. Broad Searchfox multicol searches first returned crash tests; both discovery attempts are retained rather than represented as comprehensive coverage.

## Ten-case matrix

Two column widths: outer260→columns120 and outer140→columns60, each in a fresh fixture. Five variants: original empty table; nonempty20px solid child; forced third-row column break with empty cells; forced third-row break plus solid children; ordinary block-row control. All visible, no hidden state, no flex/OOF query repair, no fonts, no mutation. Four rows20px in a40px-high two-column container. Exact two-column row/cell/table rectangle assertions are calibration targets; failed table cases are unsupported/unreached fixture coverage for the hidden-provider campaign, not automatically newly filed bugs.

All raw rectangles, provider/table fragment lists and computed row break values are recorded before assertions in window.tableFragmentCalibration. Root can collect them even for failed testharness subtests. Ordinary block controls distinguish a table-specific failure from broken multicol dimensions. Nonempty content avoids conflating zero font/empty-cell sizing with fragmentation. No Ahem dependency is needed for this discriminator.

Recommended campaign handling: keep valid12 nonfragmented span cases; retain failed8 fragment calibration evidence unchanged. If all table variants fail while block controls pass, stop trying to infer table continuation support from this shape and report paginated provider coverage open. Do not substitute overflow rectangles for actual continuation coverage.

No browser/build/compiler/Git mutation or production test installation by this author. Root owns calibration execution after restoration. This artifact adds a proposal; it does not amend sealed assertions.
