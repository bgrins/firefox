Fix 118 is accepted for the exact 2-path Gecko/WPT patch. Adding0.5 in binary32 can change an exactly representable integer or round a value below0.5 up to1. Widen before the half-unit addition in both integer evaluation paths.

The isolated candidate passes all 37 landing cases and repairs 13 baseline failures. All prior passing outcomes and exact retained failure diagnostics are preserved across 213 testharness cases and two reftests. Three comparison builds, the restoration build and lint pass; root and independent final review verify source, index, tests and rebuilt binaries.

Source review identified the final binary32 addition; helper, symbolic and browser checks corroborated the defect and repair. Six Lean dyadic/error-bound results plus a separately reviewed Z3 finite-binary32 mismatch query; IEEE decoding, compiler and full browser refinement remain external.

Working-stack installation and signed commits remain pending. Research belongs in a preceding commit; the native commit contains only the listed Gecko/WPT paths. Adjacent counter arithmetic/grouping and generic round/sign work are outside this acceptance. No security impact or complete native verification is claimed.
