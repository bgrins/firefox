# Relative stepped-operation zero-basis probe

Source-only lead; no browser run or patch. observe.js defines one standalone async function and creates/removes an isolated iframe. It measures18 operation/unit pairs at10/0/10 basis (54 rows), with resolved-pixel, literal, fixed-absolute and actual-unit calibration elements. Font/root/container changes are confined to the iframe; targets are absolutely positioned so they do not size the query container.

Current captured generic CalcNode::ModRem simplifies by calling try_op directly. Specified calc delegates Length to NoCalcLength::try_op, which applies the operation to matching relative-unit coefficients. Round similarly computes its remainder and bounds on coefficients. Thus the zero-basis singularity is source-reachable without any new parser grammar or unresolved easing policy. Direct division uses canonical-value knowledge and is a preservation control, not presumed defective.

No API initial-independence inference follows merely from these widths. A fix must preserve unsupported/contextual nodes until operands are known and audit cross-consumer representation boundaries; existing integer/easing prerequisites still apply if formerly folded counts become deferred. Do not change general try_op, since ordinary unit-preserving sum/product operations legitimately use it. An operation-specific knowledge guard is the likely seam, subject to actual runtime and all early Round branches.

Known accepted mod/rem infinity and finite-quotient fixes are retained in the current source capture. The held Round infinite-value shortcut remains separate. This packet neither accepts a new bug nor advances canonical formal coverage. It creates no native/index/build/runtime changes.

Run in an owned blank browser tab by evaluating observe.js and then awaiting observeRelativeSteppedZero(). Preserve raw rows before interpreting mismatches; inspect support and all calibration columns.
