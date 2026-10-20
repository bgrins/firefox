# Horizontal relative-offset mutation: negative result

Thirty cases per browser compare shifted versus zero-offset geometry for row/column flex and ordinary block layouts, fixed80px overflow subjects versus auto-size normal subjects, and zero/±17px inline/block offsets. Release and restored project rows are identical. Every initial geometry calibration, translation, size preservation, unrelated-item preservation and restoration check passes.

The fixture performs a zero-offset layout before changing offsets. It therefore exercises a dynamic positioning path, unlike the earlier child-mode fixture that lays out nonzero offsets initially. The retained helper-source hypothesis is limited to its reflow-placement path and must not be generalized to all positioning updates. These results disconfirm that broader hypothesis. Next is a fresh nonzero layout versus dynamically shifted comparison at identical final DOM/styles, with horizontal and vertical controls.

No new bug is accepted or counted. Browser/source pins are stable, private profiles are removed, and this probe changes no native source. The earlier final-width candidate remains independently scoped.
