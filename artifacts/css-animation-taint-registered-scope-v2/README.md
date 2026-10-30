# Registered scope V2: hidden diagnostics

This successor preserves V1. Its only HTML change is adding `hidden` to the diagnostic pre element. The complete inline JavaScript, four modes, registration calibration, sample order, assertions and timeout behavior are unchanged. The exact fixture delta is retained; the genuine subset manifest is regenerated for the new bytes. V1's source/spec audit and limitations remain applicable through REFERENCES.json.

Root reports V1 Firefox execution29669/c589ef/0 completed transport/cleanup, but observation was incomplete: harness status2. The first three modes captured both four-read phases with reference checks; literal captured only its initial four reads before timeout. That is not a successful four-mode run. Root independently verified cleanup8e5462/0. No Chrome V1 result exists in this preparation.

Hypothesis: pretty-printing the growing visible pre before the iframe moved a later iframe offscreen and throttled requestAnimationFrame. Hiding diagnostics removes that potential layout disturbance without changing the sampling code. This cause is not proved by the old timeout; new browser runs must establish whether collection completes. No timeout increase or retry of the old owner is included.

Raw records remain on window.registeredTaintObservations and in hidden pre text; the installed collector reads the object after WPT completion without getters. The prior distinction between calibration, tentative taint expectation, WPT verdict, and complete observation remains. No native/browser/Git operations were performed here.
