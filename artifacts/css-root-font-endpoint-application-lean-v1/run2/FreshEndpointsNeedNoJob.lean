import Application
open EndpointApplication
example : (refresh 64 (initial 46)).queue = [] := by decide +kernel
