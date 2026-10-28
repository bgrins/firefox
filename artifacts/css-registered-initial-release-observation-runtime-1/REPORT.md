# Release Firefox: registered initial-value admission

Installed Firefox 158.0 completes 68 named assertions with 27 PASS and 41 FAIL, and both harnesses end OK. All 41 failures pass ordinary CSS.supports calibration and then fail because CSS.registerProperty does not throw the expected SyntaxError. These are multiple probes of computational-independence admission, not 41 independent bugs.

The original 21 assertions are 12 PASS / 9 FAIL and match the complete local-baseline assertion signatures, including field presence. The expanded 47 assertions are 15 PASS / 32 FAIL. The expanded failures cover all six container units in direct, calc, later space/comma-list and later-transform forms, plus Canvas selected as a color before an identifier or literal alternative.

Passing controls include identifier-first/literal-first Canvas, the failed color alternative followed by the Canvas blue identifier list, absolute values, symbolic percentages, nested currentcolor and independent nested gradients. The five ambiguous image/normalization observations were not run and make no normative claim here.

The tested application has BuildID 20261007201254 and mozilla-release SourceStamp eb9a6e3a736802c8e080a76c44dc81f409d99d54. This is an independently inventoried installed release application, not a browser built from the experimental local sources. Current repository WPT preferences and harness were used; this is not a stock-default-profile observation. The trace for the JS registration oracle is in the sealed initial-independence probe v3; the separately unresolved @property policy is outside these assertions.

The wrapper completes with exit 0 while WPT returns 1 for the observed failures. Raw cardinality, application metadata/inventory, source/binary/index preservation and owned process/temp cleanup all pass. The exact 36-file staged research commit remains unchanged. Session43539, launch451769, terminalfe018a. No new fix is accepted and no security consequence is inferred.

Next: preserve selected grammar interpretation from validation through initial-cache computation, validate every admitted component without leaking failed-alternative dependencies, and retain the independent controls. The inactive AST inspection prototype is useful preparation but remains uncompiled and does not yet implement registration validation.
