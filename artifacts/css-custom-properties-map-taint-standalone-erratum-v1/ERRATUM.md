# Committed fix numbering correction

The sealed `css-custom-properties-map-taint-standalone-review-v1/REPORT.md` reverses the final committed numbers for the two enumeration repairs. The correct order, supplied by root, is:

- **Fix 74: live count and filtered indexed enumeration**, commit `0cac5c270615`.
- **Fix 75: nearest-owner iterator shadowing**, commit `90ffac0a5e407`.

Read the report's “74, nearest-owner iterator” paragraph as **75**, and its “75, live enumeration/count” paragraph as **74**. Historical discovery order caused the labeling error. The source snapshots, dependency arguments, candidate patch and replay results are unchanged. The predecessor seal is preserved. This erratum does not claim new source, compiler or browser validation.
