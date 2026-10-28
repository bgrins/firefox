Prepared acceptance payload for the proposed standalone registered-value zoom fix. This package is not installed or accepted.

`payload/` contains exactly seven native bodies and seven WPT pages. `fix.patch` applies them to the recorded committed base. `CLEANUP.patch` changes only the two currently modified native files with incidental formatting: two unrelated anchor-parser return semicolons are removed and one pre-existing LengthPercentage line wrap is restored. The other five candidate native files are byte-identical to the tested standalone candidate. The substantive normalization patch remains unchanged.

`PAYLOAD.json` records the immutable base HEAD, signed v23 epoch, seven original/current/cleaned native fingerprints and exact test origins. The base native bytes were independently compared with `git show` of the explicit recorded HEAD; no mutable HEAD lookup was used. Current candidate fingerprints are joined to the signed checkpoint epoch and sealed source captures, not a new live-tree preservation receipt. All six existing zoom fixtures are exact bytes from the paired standalone WPT v2 captures. The container page is exact bytes from the sealed unzoomed-source draft. No WPT expectations, metadata or body text are altered here.

The seven pages are `registered-length-zoom.html`, `registered-compound-zoom.html`, `registered-relative-length-zoom.html`, `registered-style-range-zoom.html`, `registered-animation-length-zoom.html`, `registered-numeric-style-range-zoom.html`, and `registered-container-length-target-zoom.html`, all under `testing/web-platform/tests/css/css-properties-values-api/`. They contain the existing 70 focused assertions and the 16 bounded container assertions. Shared testharness resources remain repository resources; this payload adds no metadata or prefs.

Artifact-only transport check:

```
python3 -I -S -B artifacts/css-registered-zoom-fix139-payload-v1/check.py
```

It authenticates all referenced inputs, applies and reverses the full patch in an owned temporary directory, checks all exact postimages, then applies and reverses the three-hunk cleanup against captured current native bytes. The completed run used zero offsets/fuzz and removed the scratch directory. It does not install anything or inspect a running browser.

Root must perform the guarded live transition, rebuild the cleaned native bytes, run real WPT lint and the final 86 assertions, and preserve their actual results before committing a standalone fix. The proposed fix number is provisional and no accepted count is changed. The source-container coordinate interpretation and strict published-text gap are documented in the separate decision record; no formal/native equivalence is inferred from transport checks.
