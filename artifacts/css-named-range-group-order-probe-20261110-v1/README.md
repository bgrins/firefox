# Named-range grouping browser probe

The retained optimized browser containing percentage repair #172 fails the
repeated named-range grouping case. With equal finite computed offsets of 0.5,
source groups A,B,C,B serialize as A,C,B instead of A,B,C. The unique A,B,C
control passes. The repeated group's later 30px declaration assertion passes
before the order assertion fails; assertions following that failure were not
reached.

`baseline1/RESULT.json` records two callbacks (one PASS, one FAIL) and one OK
harness ending. WPT exits 1 for this intentional unannotated failure; WPT lint
exits 0. No native source was installed and no build was run. The temporary
two-case fixture exactly matches the source investigation's proposal.

The baseline-only runner preserves the signed percentage experiment's analyzer,
process management and restoration code. `RUN-INPUTS.json` freezes executable
inputs. `ROOT-AUDIT.json` independently checks the raw result and restored
application; the separate `css-named-range-group-order-probe-review-20261110-v1`
capsule records an independent agent review, including all 9,378 application
entries, three extras, source/test pins and owned-process absence. The fixture,
backup and lock were removed. The restored browser is BuildID 20261110174523.

This is another manifestation of #172 / bug 1778402, not a new repair count.
The separate native candidate and three-case comparison require their own
runtime validation. This probe establishes neither a release exposure estimate
nor a memory-safety or performance result.
