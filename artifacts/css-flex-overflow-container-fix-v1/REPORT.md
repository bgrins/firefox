# Standalone overflow-container retiming candidate

Status: **336 TARGETED OBSERVATIONS PASS; REVIEW AND SKIP-PATH GATE OPEN**.

The candidate moves flex overflow-container reflow until after final flex output size and ordinary-item positioning are known. It passes the final physical output size to the existing helper. The standalone proposal contains only nsFlexContainerFrame.cpp and one WPT; it does not widen arithmetic or depend on the exact-fragment prototype. The runtime experiment applies only its native hunk to the shared source, preserving all existing changes.

The new WPT has 336 stage observations across three writing modes, both directions, row/column flex, four/eight items and 160/240px columns. Stages include initial layout, a same-size min-inline-size change, last ordinary item80→81→80, column-size change/restoration and reinsertion. Independent absolute reference boxes calibrate descendant geometry.

The shared baseline gives 224 PASS / 112 FAIL; all failures are vertical-rl. The candidate gives 336 PASS, preserving all 224 passes and correcting every failure. Candidate and restoration builds both exit zero. Full logs retain the known mach monitor exception. No separate release WPT run or isolated upstream browser build is claimed; earlier reduced release/project probes reproduce the underlying ordinary-size discrepancy.

These results do not prove that the skipped-overflow-container branch executes during any specific WPT stage. The separately sealed skip trace records12 helper visits, all dirty and reflowed; it does not establish skipped-child behavior. A subsequent paired eight-stage lifecycle diagnostic corrects seven baseline failing stages and preserves the shortened-chain control, without proving exact internal list operations. Source review also tracks drain/tracker/ordinary-child ordering, continuation identity, relative/orthogonal positioning, float-manager behavior and overflow union. No broad regression suite, final formatting/lint or formal acceptance is claimed yet.

The experiment restores original source and browser build, removes its temporary WPT, and verifies unchanged HEAD and the exact staged binary diff. The original shared source includes accepted pending patches and the previously rejected early packing candidate. No native repair is accepted or committed on this targeted result alone.
