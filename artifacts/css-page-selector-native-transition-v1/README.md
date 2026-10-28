# Page-selector native experiment

Root-owned two-source install and configured native build following the completed 24-case original print observation. The original has 10 failures and 14 passes; all six existing regressions pass. Neither installer nor build accepts a bug fix.

The installer preserves source identities, unrelated native bodies, root/nested indexes, ownership metadata and historical provider provenance. It updates only the two page source bodies, their owned hashes and the current epoch, with a page-specific uncompiled marker. On failure it restores the source bodies and semantic epoch. The build uses the existing owned process-group, deadline and disk-space controls, and publishes actual binary hashes and compilation status. Existing provider-v5 source is unchanged and remains unaccepted.

Independent bounded review by counter_comparison_review identified control-identity rechecks and an explicit candidate-postimage/manifest join; both were applied. Source filtering preserves separate named/nameless buckets, duplicate entries and layer order. Only a subsequent identical 24-case paired run and lint can support acceptance.
