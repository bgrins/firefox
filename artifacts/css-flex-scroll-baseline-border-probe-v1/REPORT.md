# Scroll baseline provider boundary

Testing the natural-donor proof's truthful-provider premise found an ordinary asymmetric-border regression. The unchanged 64-case probe compares equivalent visible and scrolling boxes, with first/last baseline, direct/nested block items, four border configurations and hidden/auto/scroll/clip overflow. Dimensions, internal text offsets, removal controls and restoration checks pass for every row.

Installed release passes all 64. The development build before the provider repair fails six nested last-baseline cases: start-only and end-only 9px borders with hidden, auto or scroll overflow. The offset is respectively +9px or -9px. The separate provider repair restores all 64 cases. The post-repair runner additionally pins ScrollContainerFrame.cpp; the earlier runner pinned the browser binaries and flex source but omitted that provider source. The fixture bytes are unchanged.

This invalidates readiness of the natural-donor patch under ordinary scroll providers, despite its conditional kernel proof passing. Its acceptance was withdrawn in the management ledger and commit queue; the sealed mathematical and native checkpoints are historical evidence. Provider truth was an explicit assumption, now tested rather than presumed.

The expanded v2 probe also exposes the provider defect in installed release using flex/grid scroll containers. That separates the preexisting provider defect from the new helper's additional exposure. No isolated development build without the natural patch was run; release comparison alone does not isolate every project source delta.

The candidate provider repair has a direct flex/grid WPT and a single-source paired build experiment. See ../css-flex-scroll-baseline-border-fix-v1/REPORT.md. No new security impact or fragmentation correctness claim is made.
