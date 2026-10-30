# Proposed browser cohort and remaining checks

Start with the exact original45 preservation suite plus the sealed nine-case overridden-dependency page (manifest0400dac0). Their union is 54 callbacks, five pages and seven shared resources; the execution owner must authenticate actual bytes, resources, metadata and rosters. Compare full observations and statuses against a freshly rebuilt committed original. The font target is the smallest independent witness; color cases exercise ATTR admission plus order/importance. No expected-status rewrite or assumption that prior preservation failures must improve.

Three existing tracked WPT candidates, discovered through Searchfox revision86136a5faf970e59063cd07b822717f6fd03a958, are:

- css/css-cascade/revert-rule-revert-layer.html: five combinations of rule/layer rollback (discovery9623fe). This is ordinary common-path preservation, not a substitute for variable-produced prioritary rollback.
- css/css-cascade/revert-layer-008.html: one font-size layer rollback and transition callback (full source4d6212).
- forced-colors-mode/forced-colors-mode-51.html: one callback testing color-scheme forced to light dark versus forced-color-adjust:none preserving light (full source169afe). It needs the normal forced-colors test configuration in a separate lane, not an uncalibrated default browser run.

These are upstream discovery names, not HEAD byte/metadata or accepted-fix claims. Root must authenticate the tracked files and their harness/configuration before inclusion. Historical untracked rollback snapshots are excluded from the recommendation.

New focused discriminators are still required where those pages do not exercise the new selection path:

1. A winning variable font-size with an independent literal value; lower cyclic loser must not contribute an edge. Calibrate its computed size and registered2em output.
2. font-size:var(--missing,revert) inherits through origin rollback despite lower author cyclic declarations; compare registered2em against the inherited size.
3. A higher-layer var(--missing,revert-layer) selects a lower-layer literal size and excludes losing cyclic declarations in the reverted layer.
4. var(--missing,revert-rule) selects the next literal rule and stops before a lower cyclic rule.
5. An actual active custom/priority cycle, with literal and no-cycle controls, must retain the existing invalid/default outcome and discard the prepared chain.
6. A reached Appearance-gated candidate is reconsidered, while an earlier winner prevents the lower Appearance read. This may need Gecko-specific test setup; do not invent a portable @appearance-base oracle.
7. Forced-color adjustment synthesizes rollback after a variable candidate, plus an explicit forced-color-adjust:none control. The mode and effective adjustment must be calibrated.

Also compare the rejected V1 source-shaped controls: literal font-size20px with registered --x:1em and font-family:var(--x); literal line-height10px with registered --x:1lh and writing-mode:var(--x). Preserve the acknowledged scheduling discriminator --x:<length>=1em; font-size:20px; zoom:calc(var(--x)/1px). Compare original/candidate outputs rather than assuming these cases pass or that inherited scheduling is correct. None of these new discriminators is authored or run by this package yet.

Prepared application calls neither substitute_variables_if_needed nor tweak_when_ignoring_colors; code review establishes that call-path property. Public value equality cannot establish exactly-once evaluation. Any future operational counter test must distinguish actual source execution from an extracted analogue. No mirror selector test is offered as native evidence.

Real compiler checking and the above browser comparisons remain validation gates. The narrowed V2 delta has no current concrete source counterexample from bounded peer review; broader inherited scheduling limits are explicitly outside its correctness claim. A source regression or any unexplained before/after change blocks acceptance.
