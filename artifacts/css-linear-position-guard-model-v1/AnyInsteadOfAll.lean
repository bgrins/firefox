import Guard
open LinearPositionGuard Position
example : (suppliedResolves known || suppliedResolves deferred) = true →
    allPresentResolve known deferred := by
  decide
