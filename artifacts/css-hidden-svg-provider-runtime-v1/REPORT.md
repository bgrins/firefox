# Hidden SVG matrix reproduction

The reviewed eight-case diagnostic reproduces two stale matrix results on the current local working build. After a hidden host changes from 100px to 200px, its SVG viewBox-dependent getCTM() and getScreenCTM() retain scale1 instead of2. Repeated reads are identical. The six visible/no-viewBox controls pass; all eight cases calibrate, and getBBox(), explicit viewport layout and reveal recover the expected matrices. Restoring host width recovers the original values. These are ordinary-size connected SVGs, not extreme-coordinate cases.

The visible twin and exact viewBox arithmetic provide the first-read oracle. No descendant geometry query intervenes before the first/repeated matrix reads. Full observations, including all recovery controls, are retained in SUMMARY.json and capture/payload.json. This confirms an observable stale-result lead; it does not accept a repair, establish clean-upstream/release novelty, or demonstrate a security issue.

Session71193 exited0. Root independently recounted the raw payload, checked identical before/final snapshots, and authenticated all337 live source/resource/binary/absence pins. The49 source guards, existing native edits and staged index are preserved by the runner's pre/post checks. Both installed112 WPT hashes/inodes remain protected. The owned browser group terminated and its temporary profile was removed. No native source, WPT, build or index mutation occurred. The actual restored OOF binaries remain current.

Next: prepare a focused native repair and WPT, check API availability behavior, and compare baseline/candidate with adjacent SVG geometry controls. The accepted count remains112.
