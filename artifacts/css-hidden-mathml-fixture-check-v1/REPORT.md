# Hidden MathML query diagnostic

Eight exact cases completed with six PASS and two FAIL; the harness finished OK. All four visible controls and both root-block hidden controls passed. Neither failure was a calibration or feature-support failure. WPT lint passed.

Both failures involve an internal hidden mrow owner after changing its CSS width from 100 to 60. The mrow-first query expected [30, 10, 40, 16] and returned [70, 25, 0, 0]. The mspace-first query expected the same rectangle and returned [70, 25, 40, 16]. These are the first reported mutate-stage assertions; no unreported later assertions are inferred.

This is a reproducible lead on the restored working build, which includes older prototypes and the three accepted unsigned repairs. It is not an isolated upstream comparison or an accepted bug. Native frame identity, used content-visibility, dirty-state transitions and the MathML hidden-return attribution still require investigation.

No native sources or index were written and no build was run. Root verified all 34 source guards, unchanged HEAD and 925 staged research payloads, before/final/live equality, unchanged binaries and historical resources, and absence of the owned MathML and prior float temporary tests. Cleanup completed without errors.
