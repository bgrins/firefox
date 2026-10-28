# Contextual line-height browser baseline

The exact twelve test bodies from the sealed repair proposal ran in local Nightly 160.0a1 using byte-identical in-tree testharness.js and testharnessreport.js. Harness URLs were rewritten to adjacent files and a completion callback inserted. This is a file-document observation, not a wptrunner invocation or a paired candidate validation.

Seven tests fail and five pass. Named, stepped, summed, ratio and nested-key random number line-height resolve to zero despite positive same-key length references. Sibling-index and sibling-count both give zero across insertion/removal, instead of 20/30/20 pixels. Literal, calc literal, fixed random, percentage ratio and inherited-line-height ratio controls pass. Each random test samples font sizes 10/20/10 before its assertions; the first mismatch terminates assertion evaluation, so this result does not separately enumerate later snapshots.

The harness completed without error and all fixture elements were cleaned up. The explicitly selected headless local binary had random enabled without changing its preference. The session and owned tab were closed. Full native/binary/research hashes, installed identities, canonical Lean index and the exact pending 165-file staging selection match before and after. Runtime epoch/ownership files were not changed. The binary retains its prior page/provider build provenance; the proposed line-height repair was not installed or compiled.

No accepted fix or coverage count is added. Next gates remain configured native typechecking, a linked candidate, and actual paired WPT execution.
