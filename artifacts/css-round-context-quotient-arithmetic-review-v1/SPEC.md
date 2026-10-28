# Numeric oracle premise

The current official [CSS Values 4 Round section](https://drafts.csswg.org/css-values-4/#round-func) selects integer multiples below/above the input, keeps exact multiples, and selects the upper multiple on nearest ties. Directed strategies select the corresponding bound; to-zero selects the smaller magnitude. The [argument-range rules](https://drafts.csswg.org/css-values-4/#round-infinities) handle zero steps and infinities separately. These were reread through the official draft on 2026-10-28.

The [numeric precision section](https://drafts.csswg.org/css-values-4/#numeric-types) makes supported precision/range and the implementation's closest supported representation implementation-defined. Accordingly, the oracle here is conditional: exact arithmetic on represented binary32 operands, followed by nearest-even binary32 output conversion. It is not a claim that CSS mandates this machine format or every oracle bit.

The spec CLI remains unavailable as previously recorded; official web fallback was used, with no exhaustive algorithm-graph claim. No new normative finding or bug count is asserted.
