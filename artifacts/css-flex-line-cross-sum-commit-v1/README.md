# Flex line cross-size sum commit queue

Evidence and proof/review companions precede the two-file Gecko/WPT repair.
The original accepted patch applies after every queued predecessor on both
retained bases. Removing/reapplying the separate baseline-sum patch recovers
the exact standalone source, demonstrating that the two changes commute.
The real index and working tree are untouched. No isolated upstream runtime
is claimed, and the known intermittent regression remains in the evidence.

The accepted proof concerns nonnegative line/gap accumulation and conditional
size observers. Downstream packing arithmetic is a separate confirmed lead.
Signing remains required; the queue follows the sticky positional guard repair.
