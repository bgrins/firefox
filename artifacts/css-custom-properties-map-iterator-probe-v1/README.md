# Browser confirmation of inherited custom-property enumeration defect

The seven-case source-audit proposal was run on the current shared-tree Firefox
build containing the substituted-inherit candidate. Two cases fail: one and two
child overrides of a nine-entry parent map produce duplicate names and omit
other names. Five controls pass, including the eight-entry threshold and equal
values. The test checks direct values and parent enumeration before child names;
no custom-property ordering is assumed. The harness is OK and the suite ends.
Source/test/binary pins remain stable, as recorded in RUN.json.

This confirms observable behavior for the separately sealed source audit. It is
not a repaired baseline/candidate pair. No map implementation change, formal
map proof, isolated upstream build or release-browser result is claimed. The
candidate label-target correction still needs native integration, paired WPTs,
independent review and a separate standalone commit.
