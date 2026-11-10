import Obligations
open AnimationObligations
example : (install (request selected newerKey) all).queued newerKey = false := by decide +kernel
