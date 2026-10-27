# Hidden float query repair accepted

Root accepts fix109 for stale geometry of current-owner, non-pushed floats when block content is skipped. The patch marks the real Float-list subtrees; dirtying their line placeholders does not reach those frames.

The landing patch contains only nsBlockFrame.cpp and the eight-case regression WPT. Both are byte-identical to the tested proposal. Its four failures become passes with only this repair applied to saved HEAD; all four visible controls remain passing. The four extra visible multicol calibrations stay in research evidence. The independent review agrees with this reduced partition; no new runtime is implied by removing that unrelated landing file.

The earlier composed95 run preserves all79 prior controls. The standalone cost experiment eliminates480 stale reads; clean and visible geometry remain correct. First correct recovery costs more than the stale baseline, and timing precision does not support a general performance claim.

The formal model proves selected-root and conditional descendant readiness. Native ownership history, dirty-root closure, provider completion and frame lifetime remain assumptions to refine. This acceptance does not claim full float, continuation, anonymous-owner or CSS verification. No security impact is established.

Research belongs before the two-path fix commit. The candidate is not installed in the live tree while the MathML trace runs. Signing is pending; nothing was pushed.
