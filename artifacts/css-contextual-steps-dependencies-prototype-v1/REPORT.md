# Contextual keyframe easing: dependency publication

Research-only six-source successor of css-contextual-steps-keyframe-prototype-v1. The new two-source delta publishes conversion dependency effects into the real owning computed style before build. It does not activate contextual steps: the unresolved-count parser guard remains.

The retained five-source groundwork computes keyframe easing in actual Gecko/Servo contexts and reconstructs CSS keyframes on relevant normal style updates. The new handoff prevents conversion effects from existing only in a temporary animation context. Both changes remain uncompiled research; native types, Gecko/Servo integration and runtime behavior have not been validated.

Remaining activation obligations include selected keyframe declaration scope, complete style-sharing/effect invalidation, animated-style ordering and self-dependency policy, and the open API easing-context policy in CSSWG issue 14246. The range-offset resolution in issue 13853 does not settle that API question. No numeric cache or complete dependency-bearing easing representation is claimed.

Six WPT cases cover independent font/root/container/viewport contexts, pseudo-elements, and script keyframe override preservation. JavaScript parsed and six names enumerated; callbacks and browsers were not run. A separate observation-only self-font probe and a three-theorem Lean witness demonstrate a conditional two-state iteration problem, not a CSS conformance verdict. The negative control rejects one-pass stability.

Validation: exact six-path forward/reverse/reapply transport with no offsets/fuzz; Rustfmt parsing of all candidates; pinned Lean replay with all three declarations axiom-free and the false control rejected; private scratch removed. Rustfmt parsing is not type checking. No native/source/index/HEAD/runtime or canonical CSS-library edits, no acceptance or coverage increment.

Replay from repository root:

    python3 artifacts/css-contextual-steps-dependencies-prototype-v1/replay-lean.py --output /private/tmp/css-easing-proof-review-unique

The output directory must not already exist. Remove that owned output after inspection if no longer needed.
