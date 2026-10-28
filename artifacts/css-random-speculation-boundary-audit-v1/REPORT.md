# Remaining typed-parser random counter boundaries

Extend the existing random-counter repair across all seven `CalcNode` typed convenience parsers. The registered whole-alternative wrapper must remain. This is one existing bug family, not two newly counted bugs or a global parser transaction.

The source audit predicted two additional observable omissions in the earlier three-source candidate: a rejected length parse before percentage radial radii, and a rejected angle parse before a rotation vector. Root then ran the exact frozen eight-row function in local Nightly160. Both predictions were observed as explicit index2 instead of index1 and different computed values; the other six controls matched. All32 supplied expressions were supported. The root-owned browser run and preservation records are a separate sealed package; this audit did not execute a browser or change native files.

## Concrete call chains

`Gradient::parse_radial` → `EndingShape::parse` tries `NonNegativeLength` before its percentage-led ellipse path. For `radial-gradient(random(property-index-scoped,10%,20%) 30%,red,blue)`, the unsuccessful length path consumes the random counter before percentage parsing retries the same function. The final value contains one function, so its key must be `ua-background-image-1`. Current output instead contains index2. Explicit `ellipse` avoids the length-first route; a length-first radius is also a positive control.

`Rotate::parse` first tentatively parses an angle, then an axis, then an angle if needed. In `rotate:random(property-index-scoped,1,2) 0 1 45deg`, the angle attempt parses the numeric math but rejects its type, leaving a consumed index. The successful first vector component therefore gets `ua-rotate-2`; it should get index1. Putting45deg first avoids that failed angle attempt. Angle-only and named-key controls also match.

These relevant upstream `image.rs` and `transform.rs` captures are byte-identical to the exact current files captured before root's temporary typecheck. Other captured files have local differences, explicitly recorded in SOURCE-PINS; upstream file fetches are snapshots from the CLI's raw main endpoint, not a claim about a fixed release revision. The observed browser is local Nightly, not an attribution to release Firefox.

## Complete bounded implementation recommendation

The exact seven methods are `parse_length_or_percentage`, `parse_percentage`, `parse_length`, `parse_number`, `parse_angle`, `parse_time`, and `parse_resolution`. Every method owns the result of `Self::parse` and consumes it through its `into_*` conversion. A returned error exposes no successful parsed AST. Enclose both stages in the same counter-only Result transaction: restore the entry count on any returned parse/conversion error; preserve all increments on success. Existing flags, clamping, percentage hints and anchor options must remain unchanged. The source successor already prepared by the implementation agent uses this uniform boundary without expanding beyond the same three native files.

Nested wrappers restore their own entry count, preserving earlier successful random functions. A successful typed parse that is later rejected by an enclosing grammar still requires an enclosing transaction; the registered `try_parse(parse_entirely(...))` wrapper addresses that concrete path. This audit does not prove that every outer speculative parser has been covered. It also does not transact input cursors, use counters, dependency flags, panics or arbitrary side effects; existing callers retain their cssparser cursor backtracking. No new concrete successful-type/later-rejection ordinary-property witness was established in this bounded pass.

## Evidence limits

The original observations establish the defects and controls, not the effectiveness of the broadened native candidate. Exact candidate compilation and paired WPT/browser checks remain required. No accepted count, security claim or Lean/native refinement is added. The existing abstract counter rollback model remains relevant but did not automatically identify these native call chains.
