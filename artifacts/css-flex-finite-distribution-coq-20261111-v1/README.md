# Composed finite flex distribution arithmetic

The original six-clause target and its aggregate pass eighteen Coq module checks and combined coqchk on the first attempt. Seven ordered audits contain only the standard four Coq axioms listed in VALIDATION.json. The pinned target was not amended.

The theorem composes the previously checked finite-weight share proof with the constructed integer-rounding provider. It models the zero-weight division bypass, exact integer return for share one, rounded multiplication for a positive remaining share, and zero delta otherwise. It derives the valid-share premise instead of assuming it, and uses the proved integer/real correspondence instead of assuming an equality for the result.

For representable nonnegative finite weights and at most 4294967295 entries, a selected member's stored share lies in [0,1]. If integer free space lies in [-2^60,2^60], the resulting integer delta lies between min(free,0)-2^20 and max(free,0)+2^20 and fits signed64. A singleton weight-one input produces exactly the original integer free space, and zero weight produces zero delta even when all weights sum to zero. The two inherited binary64 rounding definitions are definitionally equal, as checked by rounding_bridge_target.

The retained run is owner39382 terminal4b7e7a exit0. Root validator050c33 exited0 and authenticates both complete predecessor manifests, inherited definitions, original target, every executed source and command, and exact theorem audit roster. The temporary container is absent and all compiled objects were on its removed tmpfs.

SOURCE-MAPPING.json and native-share-fragments.txt record a manual comparison to the current ResolveFlexibleLengths branches. This is not a native refinement proof: grow-factor promotion, acquired values, shrink-base and prefix-history correspondence, actual IEEE instructions and runtime rounding mode remain open. The genuinely nonfinite path is outside this finite-branch target. Coq-to-Lean transfer remains unchecked, so this theorem must not be inserted as an assumed Lean axiom. No Firefox source changes or new browser bugs are claimed.

Reproduce with launch.py and a fresh attempt number using the existing pinned isolated Coq image. The original attempt and validate.py provide the retained acceptance evidence.
