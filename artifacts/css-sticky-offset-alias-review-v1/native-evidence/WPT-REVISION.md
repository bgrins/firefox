# Standalone WPT refinement

The first80-case WPT completed with32FAIL/48PASS andstablepins. Its wrapper expected24failures by a counting error, so the originalcomplete=false receipt is preserved. Four overflow-producing values across four sides and two scroll offsets correctly predicts32failures.

The landable test explicitly sets the opposite edge to0px. This preserves the reference coordinates while ensuring both sides participate on the repaired implementation, so the far-side scroll cases do not depend on the separate pending fix for automatic opposite insets. The initialauto-opposite fixture and raw results remain inbaseline-wpt-v1/inputs. Version2 has the corrected32-failure gate and a new baseline; this is a semantic fixture revision, not a rerun of identical inputs.
