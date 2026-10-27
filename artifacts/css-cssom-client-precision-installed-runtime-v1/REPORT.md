# Client precision with fix 112 installed

Session 81327 exits zero. All eight cases and 32 phases calibrate exactly; first/repeat/restored measurements remain stable. Scroll dimensions now match all eight cases in every phase. Client dimensions still mismatch the two large-plus-17 cases (16777218 instead of 16777217), with all eight reset cases recovering. Client origins remain correct zero controls.

Exact recursive comparison against the pre-installation capture finds only six scalar changes: the two scroll dimensions in first, repeat and restored phases now return 16777217. Every other payload field, including client dimensions and independently calibrated geometry, is identical. This isolates the remaining client conversion issue in the mixed working build; it does not establish a new accepted fix, release prevalence or large client-origin failure.

The installed source, 318 resource/binary pins, existing WPT inode and full index/925-stage state are preserved. Owned browser-group cleanup and profile removal succeed. No source, test, build or index mutation occurs in this probe. The client repair remains an unaccepted extension proposal for the still-unsigned integer-geometry fix.
