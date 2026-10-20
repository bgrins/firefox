# Focused follow-ups

These are coverage suggestions, not newly discovered failures or extra prerequisites inferred solely from missing tests.

1. RTL: duplicate the calibrated matrix with direction rtl; logical inline coordinates must measure from the appropriate physical edge. Do not merely negate expected offsets while keeping LTR coordinate extraction. Parent is already running this matrix.
2. Percentage inline offset: use an explicitly calibrated 100px containing-block inline size and `inset-inline-start:17%`, with an otherwise identical 17px twin. Keep block-size indefinite behavior out of this calibration. Change the definite inline size and compare to a freshly created twin to exercise current versus predecessor offset acquisition.
3. Auto/end-side: set inline-start to auto and inline-end to -17px; compare to inline-start17px/endauto. Both start/end auto must match the zero-offset reference. An overconstrained start17px/end31px case must follow containing-block start-side precedence, not a hand-invented average.
4. Property lifecycle: relative17px → static → relative17px with layout flush each step, then compare with a fresh relative twin; repeat zero-first. Changing `position` may reconstruct/reflow, so this is a lifecycle test, not proof that the optimized update path ran.
5. Sticky controls should compare old/candidate outcomes, not require relative's constant translation. No sticky offset is newly applied by the candidate.
6. Caller-specific fieldset/grid/table/canvas fixtures require a demonstrated overflow continuation; mere multi-column layout with no actual OC path cannot close this coverage gap. Root's retained block/grid/fieldset CSS Break tests can detect regressions but cannot alone certify each caller path executed.
