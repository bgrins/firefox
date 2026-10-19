MUTATIONS = {
    "RemoveIdentity": (
        "  else if isFinite a && isInfinite b then a\n",
        "",
    ),
    "AcceptInfiniteDividend": (
        "  else if isFinite a && isInfinite b then a\n",
        "  else if isInfinite b then a\n",
    ),
    "ApplyModExceptionToRem": (
        "def native (formula : Formula α) (op : Op) (a b : Number α) : Number α :=\n"
        "  if op = .mod ∧ isInfinite b ∧ sign a ≠ sign b then .nan\n",
        "def native (formula : Formula α) (op : Op) (a b : Number α) : Number α :=\n"
        "  if isInfinite b ∧ sign a ≠ sign b then .nan\n",
    ),
    "EraseZeroSign": (
        "  else if isFinite a && isInfinite b then a\n",
        "  else if isFinite a && isInfinite b then\n"
        "    match a with\n"
        "    | .finite (.zero _) => .finite (.zero false)\n"
        "    | _ => a\n",
    ),
}
