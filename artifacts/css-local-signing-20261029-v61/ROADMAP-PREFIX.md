## 2026-10-29: pow exceptional-value final validation complete; native acceptance pending

The exact pow candidate source and proposal-v3 24-case WPT completed reversible
and installed validation at harness HEAD 20ab7e723b66. Original 17634/873fe7/0
recorded 129 PASS and 18 FAIL; reversible candidate 87473/6a91a5/0 recorded
147 PASS, preserving 129 control and two ending signatures. Its child exit 1
was caused by twelve obsolete expected-FAIL annotations becoming unexpected
PASS. The owner restored source/app, removed its backup and preserved state.
The raw-index observation was separately reconciled by 70897/616aee/0; no
cause for that byte-level drift is claimed.

Root then installed the exact tested source/WPT and archived/deleted only that
stale metadata. Installed lint 47346/4c7a58/0 reported no errors or warnings.
Final build 44703/db4c6b/0 and installed comparison 88239/b98618/0 passed:
147 PASS, zero FAIL, two OK endings, no unexpected results, and all 131 strict
control/ending signatures plus every originally passing signature preserved.
Both original/final raw logs replay exactly; source, state and app metadata
were preserved. The four strengthened authored sign observers distinguish
negative infinity from NaN after opacity clamping; historical proposal v1/v2
fixtures remain separately recorded rather than rewritten.

V61 signs this research, actual validation, independent reviews and disabled
publication tooling before native acceptance. Counts remain 148 accepted fixes
through tracked ID 149, excluding held fix 120. The pending standalone payload
is exactly calc, the new WPT and stale metadata deletion. Historical accepted
Hypot 149 and round 145 provenance remains intact; current calc supersession
is explicit. Only the subsequent reviewed signed native commit and ledger
publication may accept prospective fix 150 and increment the accepted count.

The abstract guard/folding and binary32 classification companions have bounded
claims. They do not prove native powf, correct rounding, full CSS conformance
or a canonical coverage increment. Shared-branch validation includes the held
provider; no clean-upstream execution is claimed. Contextual easing remains
unaccepted despite its recorded 315-case comparison and isolated Servo checks;
its ownership/native-refinement limits remain in force.

Earlier roadmap follows unchanged.

