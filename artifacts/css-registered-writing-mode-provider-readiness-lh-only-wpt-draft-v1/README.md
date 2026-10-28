# Line-height-only readiness reduction

Separate unexecuted16-case fixture. It preserves the original four families, declaration/query orders, exact test names, registration names and sequence numbers. The only changes are the title, both mixed-length declarations from calc(1lh+100vi) to1lh, and the two length/geometry expectations from LH+180 to LH. REDUCTION.patch records the complete delta.

The invalid registered keyword provider still reads present bogus via var(--ready,1vi); its1vi fallback remains present but unused. There is now no selected logical-unit dependency in the consuming registered length: independent fixed line-height40/60/40 produces40/60/40px. The keyword registration must still default to its noninherited vertical-rl initial, and writing-mode must consume that computed keyword. Literal writing-mode, literal registered keyword and used-keyword-fallback controls are preserved. The ordinary length sibling is also1lh, avoiding an unrelated mixed-length calibration.

Root reported two failures in the preceding mixed fixture (invalid-provider IDs8/9, provider-first declarations and both query orders), with providerV/WMH and360/380/360px against220/240/220px ordinary controls. This reduction has not run and does not imply the same graph iteration order will recur. Preserved names improve comparability but are not a guarantee about map iteration. A failure here with providerV/WMH and otherwise correct40/60/40px isolates readiness from selected logical-axis computation. A pass cannot by itself prove readiness safe.

The original sealed ORACLE.md and pinned official API/Values4 source establish registration-invalid defaulting, computed-provider substitution and fixed-lh semantics. No genuine reciprocal vi cycle is asserted. No original32fixture, runner, native source, canonical WPT, Git/index or runtime epoch was modified; there is no new accepted-bug claim.

Static node syntax and exact16-name enumeration ran without invoking callbacks. Temporary outputs were removed. This is a draft for the next isolated browser observation, not browser validation.
