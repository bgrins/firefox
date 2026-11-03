import RouteAdmission
open SelectiveRouteAdmission CancellationRoute CancellationHandoff
example : FontUnitAdmission.admits FontUnitAdmission.idOwner true true false FontUnitAdmission.empty 7 = true := by decide +kernel
