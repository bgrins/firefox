# Computed-keyframe conformance baseline review

Independent raw-result/full-restoration audit passes and the runtime hold is released. The exact vector is three PASS, five FAIL, one OK; lint exits 0 and WPT exits 1. Crucially only FOUR failures reached getter assertions. The animated-font callback fails its setup read: expected 15px, actual 10px. Its subsequent 15px/30px getter assertion was never executed. Counts alone do not establish that coverage.

| Callback | Actual failure stage/value |
| --- | --- |
| marginLeft | Getter array expected 16px/32px, returned 1em/2em |
| registered length | Typed static registration setup passed; getter array expected 16px/32px, returned 1em/2em |
| unregistered reference | Getter array expected 12px/12px, returned var(--source) twice |
| changed source | Getter array expected 24px/24px, returned var(--source) twice |
| animated font | getComputedStyle fontSize setup expected 15px, got 10px; getter assertion not reached |
| unregistered tokens, WAAPI, replaced CSS | All PASS |

The four getter failures reproduce the intended computed-value return gaps. The font observation needs a separate bounded timing/style diagnostic before changing that oracle or treating it as a getter failure. Nearby held font work is not established attribution: this is the animated target's own font, not simply a descendant relative dependency. Pending pause, synchronous sampling, getter-triggered flush, ready/reseek and explicit rematch must be distinguished. Existing v1 fixture/evidence remain immutable.

The reviewer separately reconstructed raw lifecycle/status/message records and matched all nine saved rows, including exact failed-assertion stage. Frozen execution manifest 617320dd8248f252a83144341486649e5d53ec603a1ecd82fd79ca017363f068 and HEAD ec467c0219d3d5daf70f42fcc53677cf8a262173 authenticate the run. All 9,378 app entries, three extras, seven retained source/test paths, binaries, configuration, test pins, logical index and HEAD match. Owned process groups, temporary fixture/metadata, backups and lock are absent. Full logs contain familiar nonfatal SWGL framebuffer/Nimbus diagnostics, no harness crash/timeout/loss. No native build ran.

Root executed the run; this reviewer authored its wrapper and independently checks execution/restoration, not wrapper authorship. No new fix, catalogue count, source mutation or final missing-pseudo/debug acceptance is claimed.
