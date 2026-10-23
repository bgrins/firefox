# Independent cost-v2 review scope

Pending producer draft; no acceptance or browser measurements.

1. Distinguish first selected-leaf work, same-leaf repeat, other leaves, second pass, and no-mutation reads. Check exact full-rectangle calibration and separate known empty buckets.
2. Verify exact roster/checksum counts, warmup exclusion, timing units, zero/quantized samples, and incorrect geometry retained as non-equivalent work.
3. Verify process/group ownership before signaling, PID reuse/session handling, bounded waits and explicit per-operation errors. No-live-group is not automatically proof of no escaped descendants.
4. Preserve EPERM ambiguity from v1. A race-qualified cleanup result requires fresh evidence; surviving or unknown owned processes must block progression.
5. Review compact v3 integration only after cost source review: timings on four uninstrumented main variants; none on original-key variants or traces; independent source/resource stability checks and restoration on unsafe cleanup.

Review work is artifact-only. No browser, Gecko build, shared source, index, or Git mutation.
