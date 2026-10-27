Fix 117 is accepted for the exact 3-path Gecko/WPT patch. CSS-authored calculated counter values can collide with the reserved automatic-reset marker. Preserve the distinction while retaining raw HTML-mapped values.

The isolated candidate passes all 23 landing cases and repairs 14 baseline failures. All prior passing outcomes and exact retained failure diagnostics are preserved across 213 testharness cases and two reftests. Three comparison builds, the restoration build and lint pass; root and independent final review verify source, index, tests and rebuilt binaries.

Source and provenance investigation identified the collision; browser tests reproduced it. Lean models the parsed/raw exclusion contract rather than discovering this automatically. Five conditional provenance laws distinguish parsed CSS and raw mapped producers; native producer coverage and runtime behavior remain separate evidence.

Working-stack installation and signed commits remain pending. Research belongs in a preceding commit; the native commit contains only the listed Gecko/WPT paths. Adjacent counter arithmetic/grouping and generic round/sign work are outside this acceptance. No security impact or complete native verification is claimed.
