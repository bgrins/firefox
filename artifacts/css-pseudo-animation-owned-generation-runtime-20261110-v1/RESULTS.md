# Owned-generation runtime result

The optimized candidate builds and preserves all 130 selected records: 99 PASS,
19 known FAIL callbacks and twelve OK harness endings. Statuses, messages,
expected statuses and intermittent classifications match exactly between the
fresh baseline and candidate. Both WPT lint commands pass. The successful build
retains four known nonfatal Mach tier-monitor KeyError diagnostics.

Root executed the frozen experiment at `010752412bc7b2e066680918f1406e04422807a6`.
`RUN-INPUTS.json` has SHA-256
`bc1b5986bed48c68feefba3de551e4e688561a481b6c1aa22932d2143bcb76a6`.
`ROOT-RESULTS.json` independently derives the complete raw comparison without
using the runner's analyzer. `baseline1/RESULT.json` and
`candidate1/RESULT.json` record successful restoration and no transaction errors.
Independent live restoration review is recorded in the sibling
`css-pseudo-animation-owned-generation-runtime-review-20261110-v1` capsule.

The retained combined #172 browser is restored; the copied prerequisite is not
left installed. Temporary fixtures, application backups and the runtime lock
are removed. Build intermediates are outside the restoration contract.

This supports the ordinary property-generation extraction only. The explicit
owned-offset refresh method still has no production caller and was not exercised.
It does not fix the missing-pseudo issue, prove arbitrary reentrancy equivalence,
or close timing/provider/cascade/cache obligations and the separate debug gate.
`README.md` and `PREPARATION-FILES.json` retain their original pre-run description
and hashes; this result supersedes their prepared-only status.
