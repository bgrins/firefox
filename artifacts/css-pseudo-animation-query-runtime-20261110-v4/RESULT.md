# Internal query helper runtime result

The optimized candidate built successfully and passed all 208 direct Mochitest assertions across all 13 tasks. Setup, diagnostic, result and pending-state assertions all ran; no callbacks were missing or unexpected. The 130 ordinary WPT callback and harness records, including their existing failures and diagnostics, were identical to baseline. WPT process exit 1 is therefore retained as a baseline condition, not described as a completely passing WPT suite.

The run restored the source, application and installed test trees. Independent terminal review is recorded separately. This is bounded runtime evidence for the request-local internal helper. It does not accept a public CSSOM caller, transient recascade, visited-style handling, cache integration or the final debug-build transform-hint gate. It introduces no additional counted Firefox bugfix.

Earlier v1 manifest rejection, v2 compiler failure and v3 fixture setup exception remain separate historical records. V4 changes only the unresolved progress-timeline fixture seek to a percentage; all native inputs and all 208 assertions are preserved from v3.
