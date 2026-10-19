# Substituted inheritance invalidation lead

Source inspection finds INHERITS_RESET_STYLE added for direct registered inherit but not the substitution-produced inherit branch. ElementData requires that bit for RECASCADE_SELF_IF_INHERIT_RESET_STYLE. Matching propagates that conditional hint for reset-only changes. The exact native reset_only setting must be established; current Searchfox snapshots are discovery context, not a claim of local whole-file identity.

The six-case diagnostic compares direct inherit, substituted inherit and substituted unset with and without a simultaneous ordinary reset-property change. It checks initial values and the updated parent before the child's final value. No browser defect or normative change is claimed before execution. This lead is separate from the explicit-inherit missing-parent-value repair.

## Browser observation

The current shared-tree build reproduces two failures: substituted inherit remains 10px after the parent changes to 20px, with or without the simultaneous padding change. Direct-inherit and substituted-unset controls pass. All six cases run; harness OK. RUN.json pins the source and binary before/after. This is a reproduced lead, not an accepted repair.
