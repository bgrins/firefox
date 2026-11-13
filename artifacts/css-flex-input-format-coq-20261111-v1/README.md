# Encoded flex-factor input proof

The original six-clause target and aggregate pass20 Coq module checks and combined coqchk on the first attempt. Seven exact ordered audits use only the standard four Coq axioms in VALIDATION.json. The target was pinned before proof construction and unchanged.

The input factor is Flocq's encoded binary_float24/128, with explicit finiteness and nonnegative real interpretation. The proof derives its upper bound and exact binary64 representability; neither is assumed as a real-number premise. Every signed32 integer base is exactly representable in binary64. These facts establish the weight preconditions of the composed finite distribution theorem, including its zero-weight and exact-one distribution branches, signed64 delta safety and existing error envelope.

InputValid requires nonnegative bases only in the shrink branch. The positive grow witness deliberately uses a negative signed32 base, while the shrink witness uses base1; both encoded factors represent1. This avoids silently restricting growth merely to make the shrink proof easy.

The actual GetWeight source separately returns zero for a zero shrink base. The new inputWeight definition uses the finite rounded product in that case. An explicit branch-equivalence lemma remains to connect those forms; the genuinely nonfinite infinity-times-zero case is not represented by the finite theorem. The finite predicate is essential because B2R alone maps nonfinite encodings to real zero and cannot describe their native behavior.

Owner67417 endedff3b46 exit0; validate.py6433ad exited0 after authenticating the complete predecessor capsule, inherited sources, exact original target, all21 commands and seven audits. The temporary container is absent and its compiled tmpfs objects are removed. Discovery coqtop logs retain missing-name diagnostics and are not counted as proof acceptance.

This establishes mathematical input-format and conversion facts under Flocq semantics. Native float-field decoding, acquired base/history correspondence, exact operation/branch refinement, runtime rounding mode and checked transfer into Lean remain open. It is not a compiled Firefox proof or a new browser bug. SOURCE-MAPPING.json pins the manually inspected GetWeight source.
