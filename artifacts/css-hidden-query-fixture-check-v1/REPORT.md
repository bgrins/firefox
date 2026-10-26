# Hidden-query fixture diagnostic

Completed on the restored working build, including preserved older native prototypes. This run validates fixtures and identifies leads; it does not isolate or accept a native repair. No native source edits or compilation occurred.

- Grid: four visible controls PASS; four hidden cases FAIL at the width-change query. Direct item width remains 200 instead of 120; leaf width remains 100 instead of 60. Both bounding and offset APIs reproduce. Visible, outer, and restoration calibrations pass.
- Auto-skipped column scrolling: all four cases PASS, including col/colgroup and width changes. Each test requires the skipped-state event and calibrated scroll/geometry outcomes. These are useful regression controls, without proof of internal branch coverage.
- Fragmentation: both ordinary block controls PASS; all eight table fixtures FAIL the visible fragmentation calibration. Empty/nonempty cells and forced breaks do not produce the expected second column. This agrees with the audited multicol path disabling table splitting; table continuation coverage remains unreached.

All 22 rows and three OK file ends are retained. WPT returns 1 for the expected diagnostic failures. The driver returns 0 after complete collection and restoration. Source/HEAD/index snapshots and binaries remain unchanged; three temporary tests were removed. Grid source was separately pinned before and after.
