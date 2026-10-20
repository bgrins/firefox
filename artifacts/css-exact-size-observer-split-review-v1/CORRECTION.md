# Correction to sealed observer repair proposal

The sealed css-exact-size-observer-repair-proposal-v1 REPORT.md claims 52 WPT subtests. Its actual script registers **28**: 2 axes × 3 sizes × 2 host sizes × 2 padding states = 24 parameterized tests, plus four coordinate-effect controls. Multiple rectangle assertions within a test are not additional tests. The source file, its SHA-256, and all preserved calibration results are unchanged.

The earlier draft messages claiming 36 tests before the third size was added were also incorrect: those drafts registered 20. Only the sealed final 28-test file is the handoff candidate. This correction neither relabels failed results nor changes the required acceptance contract.

Target FILES: e004c9cb0243fbe6ecf0c74d48d84eb87e5c64e4dec72e5c6a3dad87372dfbd1.
Target FREEZE: 1489c152703a3e9a681716ac35ef910d92b11228dd88501330d5f0ab9e9b4056.
Target test SHA-256: eae84822829217092bb434350c450bf227c9cb83b3e42a57aa566e6c7985ad89.
