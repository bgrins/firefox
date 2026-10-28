import Guard
open LinearPositionGuard Position
example : oldGuard known deferred = true → allPresentResolve known deferred := by
  decide
