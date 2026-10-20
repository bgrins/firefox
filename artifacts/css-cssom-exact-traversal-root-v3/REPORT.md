# Optimized exact traversal: root source review

Root authenticated the sealed producer, reviewed the complete v2-to-v3 source
delta and the unchanged function prefix, and checked the other three native
snapshots are byte-identical to v2. The live tree remains at the originals.

The common-mode dispatch preserves flags and viewport semantics. SafeAdd uses
local temporary results; arithmetic failure restarts before publishing exact
metadata. The SVG mask matches the actual accessor, and each ancestor-context
comparison remains. No narrower exact domain was introduced to reduce cost.
The extracted replay remains conditional on its provider facades. This review
is not a kernel proof of C++, nor a build, browser or performance result.

The next local experiment uses the same six benchmark topologies with 100,000
iterations per batch and 11 samples. This changes the 1ms timing increment from
50 to 10ns per call. Fresh surrounding baselines are required; old v2 timings
are not reused as paired measurements. Fixed phase order and two processes per
phase still limit interpretation. DOMRect is explicitly captured in each WPT
run to avoid the previous run's source-snapshot omission.
