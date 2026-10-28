# Counter rollback fixtures: original browser calibration

Both sealed WPT proposal bodies ran unmodified in local Nightly160.0a1 with byte-identical in-tree harness files. Only resource URLs were made adjacent and a completion callback inserted. This is a file-document observation, not a wptrunner run or candidate comparison.

Ordinary19 gives7fail/12pass: opacity, length line-height, repeated filter factors, repeated border-image-slice members, conic-angle stops, radial percentage-first radii and rotate vector-first parsing expose wrong specified cache indexes. In particular repeated members use2/4 instead of1/2. The twelve controls pass, including the deliberately specified-only number line-height control; its unrelated computed-zero defect is not treated as numeric calibration.

Registered20 gives8fail/12pass: length-first, two failed types, failed list, and trailing-token list each fail in both initial and literal-initial declaration modes. Harness status is0 for both pages, and owned fixture cleanup completed. Named/fixed/property-scoped/successful-list controls pass.

Full source, binary, research, nested index and the exact pending165 staged files match before/after. Random was already enabled on the explicitly selected local binary; no preference was changed. Both tabs and the owned browser session were closed. No candidate source or binary was installed. All results belong to one counter-rollback family; no accepted count increases.
