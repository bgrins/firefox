# Compact hidden-layout runtime

Completed six uninstrumented58-test phases and two12-test absolute trace phases. All50 proposed landing tests pass with both repairs; four new column/group probes remain failing. Each selected repair pair has zero regressions. See ../css-hidden-layout-compact-analysis-v3/REPORT.md for exact comparisons and limitations.

Three cost-v2 timing runs complete. The combined run returns no observation by its75-second deadline, with stable inputs and fully verified owned-group cleanup. Its incomplete timing does not constitute acceptance or a native-hang diagnosis. The parent deliberately continues WPT/trace phases only after those integrity/cleanup gates pass.

The experiment exits0 after restoring all26 guarded source bytes, all temporary test absences and its original HEAD/index; the restoration rebuild exits0. ROOT-FINAL-CHECK.json independently rechecks this. The saved20 native prototypes and existing committed fixes are installed again. No repair is accepted by this experiment.
