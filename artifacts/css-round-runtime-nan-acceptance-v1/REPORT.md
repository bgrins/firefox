# Accepted fix 125: Propagate NaN before resolving round() infinity cases

The independent runtime_nan_only phase repairs 8 failing assertions and passes all 10 landing cases. The complete comparison covers 1,484 assertions and eight rendering references per phase; every other outcome is unchanged. Composition repairs all twelve targets and preserves both singles. Root session 27331 and independent terminal review verify full original-stack restoration and fixture cleanup.

The standalone patch contains only generic calc.rs and its own WPT. Scratch application/reversal and source dependency review support independent landing on HEAD90, with no pending integer/raw-length prerequisite found. The browser run uses the installed working stack; a clean HEAD90 browser run was not performed. Neither this repair nor its WPT remains installed after comparison restoration. Signing and permanent installation are pending.

The special-value class model and extracted runtime helper exposed the NaN-priority mismatch; the browser tests establish an observable eager-division route. Lean proves the supplied classifier laws, with native/IEEE/compiler correspondence remaining separate.

This is a numerical conformance repair with visible opacity consequences; no security impact is established. Keep its research/tooling in a preceding commit and its Gecko/WPT patch in one separate commit. No commit or push is claimed here.
