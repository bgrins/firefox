MUTATIONS = {
    "DropUnknownUpper": (
        "| _, _, _ => .clamp a b c\n\ntheorem fold_sound",
        "| _, _, _ => a\n\ntheorem fold_sound",
    ),
    "CensorUpperNaN": (
        "| .nan, _ | _, .nan => .nan\n  | .value x, .value y =>\n      if rawCompare x y == .gt",
        "| .nan, _ => .nan\n  | a, .nan => a\n  | .value x, .value y =>\n      if rawCompare x y == .gt",
    ),
    "CensorLowerNaN": (
        "| .nan, _ | _, .nan => .nan\n  | .value x, .value y =>\n      if rawCompare x y == .lt",
        "| .nan, b => b\n  | _, .nan => .nan\n  | .value x, .value y =>\n      if rawCompare x y == .lt",
    ),
    "CollapseSignedZeroOrder": (
        "| .finite a, .negZero => a < 0",
        "| .finite a, .negZero => a ≤ 0",
    ),
    "CensorNestedNaN": (
        "def simplify : Expr → Expr\n  | .literal n => .literal n",
        "def simplify : Expr → Expr\n  | .literal .nan => .literal (.value (.finite 0))\n  | .literal n => .literal n",
    ),
    "LoseZeroScaleSign": (
        "| .finite a => if a < 0 then .negZero else .finite 0",
        "| .finite _ => .finite 0",
    ),
    "AcceptRelativeInfinityAtZero": (
        "if basis = 0 ∧ finiteScalar a = false then .nan else .value (scaled basis a)",
        ".value (scaled basis a)",
    ),
}
