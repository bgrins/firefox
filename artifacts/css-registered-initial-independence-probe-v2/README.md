# Initial registration probe expansion

Two WPT pages provide 67 named assertions: the original 21 unchanged and 46 additions. The additions cover six ordered/literal Canvas choices, all six container units in five forms, and ten independent list/transform/color/image controls. Every expected rejection retries the same name with a valid independent initial value.

The separate report-only page has five ambiguous image/normalization observations. It is not a WPT testharness page and contributes no required PASS/FAIL outcomes. Its JSON result is available in the DOM and window.initialIndependenceObservations for a later isolated observer.

Only testharness.js and testharnessreport.js are required by the two WPT pages. No new preferences, metadata or external network resources are introduced. Ordinary grammar support is asserted before the registration result. Existing WPT preferences may still affect support; a baseline browser run is required before attributing failures.

This package contains fixture preparation and primary-spec oracles only. No browser callbacks, native build, lint, source/index/epoch mutation, acceptance or new Lean coverage is claimed. Pending signing selections are untouched. A future runner must preserve the actual staged index rather than assuming empty staging.
