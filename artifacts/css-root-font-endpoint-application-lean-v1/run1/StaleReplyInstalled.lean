import Application
open EndpointApplication
example : (dispatch staleThenCurrent).installed.value = 48 := by decide +kernel
