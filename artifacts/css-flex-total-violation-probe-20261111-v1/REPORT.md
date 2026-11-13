# Flex total min-violation candidate

Two identical release Firefox 158 captures reproduce 12 discrepancies and 8 passing controls across four flex directions. This candidate concerns totalViolation sign selection during flexible length resolution; it uses neither gaps nor margins. The observed first subject has a small final size and its rectangle/computed-style sizes agree. Every large primary item's computed size equals its requested minimum.

The original probe placed the subject after the large items. Its bounding rectangles were clipped at extreme positions, including a three-item case whose correction sum fits signed32. That probe and raw capture are retained as a rejected observation method. Moving the subject first isolates the sizing result: three ten-million-pixel primaries pass, while four/five/seven fail. A five-item 1000px control passes. The probe's primary size reads also use computed style to avoid huge-coordinate clipping.

The later 28-case WPT adds 357/359-item scaled cases and confirms 16 FAIL / 12 PASS in the existing local build. See ../css-flex-total-violation-repair-20261111-v1/SPEC-TRACE.md for the derivation and native candidate. No fixed-bug claim follows from these captures. The owned browser tab was closed; the preexisting blank tab was preserved.
