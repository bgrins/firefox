import RouteAdmission
open SelectiveRouteAdmission CancellationRoute CancellationHandoff
example : FontUnitAdmission.admits FontUnitAdmission.idOwner false true false FontUnitAdmission.shared 7 = true := by decide +kernel
