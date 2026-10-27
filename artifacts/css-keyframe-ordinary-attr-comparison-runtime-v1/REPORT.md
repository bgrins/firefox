# Ordinary keyframe attribute initialization comparison

The local three-phase comparison completed successfully (68019 exit 0). All 116 subtests and 15 harnesses completed in each phase: 95 PASS/21 FAIL → 113 PASS/3 FAIL → 95 PASS/21 FAIL. The restored normalized outcomes equal every baseline outcome exactly, including messages and expected/intermittent metadata.

The candidate repairs 18 calibrated assertions: 16 of the 24 landing cases and two distinct-URL provenance probes. All 28 mandatory landing/provenance cases pass. All 84 prior-fix/existing-animation controls retain their outcomes; all 70 assertions for prior attribute/taint repairs remain PASS. The direct-var context diagnostic and its two independent controls remain exact. The attr(var()) context diagnostic advances from provider calibration failure to a calibrated current-context mismatch; this is explicitly observational and earns no repair credit. The broader animated-custom-property context problem remains.

The distinct inert data URLs identify the baseline's literal fallback route, not an attribute-origin request. The candidate rejects the present-attribute URL while preserving the missing-attribute literal fallback. This does not demonstrate network exfiltration or establish a universal taint theorem.

Both native builds exit 0. Each log contains four nonfatal export-tier KeyError logging failures; BUILD-LOG-REVIEW records them. Two Rust sources were changed and restored exactly. Three exclusively owned WPT fixtures were removed after process-group cleanup. Original sources were rebuilt and all 116 baseline outcomes reproduced.

Root verification44157 exits0 and independently verifies the scientific comparison policy and complete raw lifecycle, while reusing explicitly identified calibrated assertion parsers. It checks761 file/absence roles,80 source guards,44 existing modified native paths,26 installed test identities and925 staged/working research payloads. HEAD and semantic staging are unchanged. Raw index bytes remain75dd5be919c4f15c10f69e5be2843b1fa347e34566e10c0713ec009935674e9b across this comparison and the root check. Older raw-index discontinuities remain separate historical limitations.

This capsule establishes the measured local comparison and restored state. Acceptance, installation and signing are separate steps. The patch addresses initial ordinary keyframe attribute lookup, not later attribute mutation registration, inactive replay, arbitrary animated custom context, or other animation entry points. No clean-HEAD90 browser run or performance result is claimed.
