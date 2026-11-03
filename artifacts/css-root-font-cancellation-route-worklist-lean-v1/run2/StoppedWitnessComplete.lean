import Route
open CancellationRoute
example : CancellationDelivery.reached (visitWitness deepRoute prematurelyStopped) = true := by decide +kernel
