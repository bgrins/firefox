MUTATIONS = {
    "IdentityInterpolation": (
        "  | .interpolate _ _ _ => .error .unsupportedDeferred",
        "  | .interpolate _ _ _ => .ok alg.identity",
    ),
    "IdentityAccumulation": (
        "  | .accumulate _ _ _ => .error .unsupportedDeferred",
        "  | .accumulate _ _ _ => .ok alg.identity",
    ),
    "IgnoreFailedTail": (
        "      (eager alg a) (eager alg b)",
        "      (eager alg a) (match eager alg b with | .ok m => .ok m | .error _ => .ok alg.identity)",
    ),
    "ReverseListOrder": (
        "  | .append a b => combine (fun x y => .ok (alg.compose x y))\n      (eager alg a) (eager alg b)",
        "  | .append a b => combine (fun x y => .ok (alg.compose y x))\n      (eager alg a) (eager alg b)",
    ),
    "DropLeftFallback": (
        "  | .error _ => deferred op left right",
        "  | .error _ => deferred op .empty right",
    ),
    "DropRightFallback": (
        "  | .error _ => deferred op left right",
        "  | .error _ => deferred op left .empty",
    ),
    "SwapInterpolationOperands": (
        "  | .interpolate p a b => combine (alg.interpolate p)\n      (partialEval alg a) (partialEval alg b)",
        "  | .interpolate p a b => combine (alg.interpolate p)\n      (partialEval alg b) (partialEval alg a)",
    ),
    "DropPercentageDependency": (
        "  | .length pixels percent => if percent = 0 then .ok (alg.translate pixels)\n      else .error .needsContext",
        "  | .length pixels _percent => .ok (alg.translate pixels)",
    ),
}
