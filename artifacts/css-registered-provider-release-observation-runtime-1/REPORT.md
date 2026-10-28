# Release provider-readiness observation

Installed Firefox 158.0 (BuildID 20261007201254; release SourceStamp eb9a6e3a736802c8e080a76c44dc81f409d99d54) reproduces the registered-provider readiness discrepancy: 28 PASS and four FAIL across the unchanged mixed16 and line-height-only16 pages. All 32 full assertion signatures match the prior local observations, including failure messages.

In both failing declaration/query variants, the provider computes to vertical-rl while the consuming writing-mode remains horizontal-tb. With 1lh alone, widths correctly follow 40/60/40px; with calc(1lh + 100vi), widths are 360/380/360px while literal vertical controls are 220/240/220px. This establishes the observed discrepancy outside our branch, independently of the accepted zoom changes.

Both page lifecycles completed; source/index/binary/application identities were preserved; the owned process group is absent and the temporary profile root was removed. WPT returned 1 for expected investigative failures; the observation wrapper returned 0. This used current repository WPT preferences and harness, not a stock-default browser profile. The harness revision is not the browser source revision. No new fix or security/performance impact is claimed.

Next validate missing-reference and cyclic fallback controls, then build and compare the general provider-default repair without weakening participant invalidation.
