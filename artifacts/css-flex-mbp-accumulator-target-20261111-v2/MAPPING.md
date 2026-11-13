# Source mapping and exclusions

| Native operation | Model | Boundary |
|---|---|---|
| `mTotalItemMBP = 0` | initial zero in `oldFold`/`wideFold` | exact initialization |
| `mTotalItemMBP += lastItem.MarginBorderPaddingSizeInMainAxis()` | one `checkedAdd` per item in order | operand is supplied after acquisition; no model of overflow in its getter |
| `nscoord` versus `AuCoord64` member | old signed32 versus new signed64 check | mathematical range test; no claim a compiler emits those checks |
| full ordered item traversal | generic `List α` and `mbp : α → Int` | identity wrapper is logical; no memory refinement |
| `mTotalItemMBP + SumOfGaps()` | wide total plus supplied `gaps` | gap production, multiplication/conversion and its safety unproved |
| container minus occupied space | `checkedSub64 inner occupied` | downstream representability explicit |
| each current `item.MainSize()` subtraction | `subtractUsed usedMain` | used operands supplied; no reconstruction of freeze/reset state |

Exact native snapshots, Searchfox discovery, source arithmetic controls and compiler-policy limitations are in the authenticated predecessor `css-flex-line-native-arithmetic-assessment-20261111-v1`; `ORIGINS.json` pins its FILES and REPORT. This target reuses those snapshots without modifying or duplicating them. No proof of arbitrary browser input acquisition, current live source, LLVM code generation or machine execution is asserted.

The existing narrow `SumOfGaps` path and per-item additions are separate potential failures. They are neither repaired nor hidden by this target. Parent's proposed native change is only the MBP member type; previous signed-collection and baseline/cross-axis fixes remain separate.
