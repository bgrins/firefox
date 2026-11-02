# Selected line-height readiness: concrete next boundary

A progress repair needs two distinct operations: compute the retained selected `line-height`, then determine what reading that final value as `lh` needs. The current aggregate unit mask cannot express this distinction. This package is a source-driven design and an exact-provider collision experiment, not a native repair, browser result, or new scheduler proof.

## Actual conversion boundary

`LOCAL-SOURCE.json` authenticates the local implementations and the sealed ordinary-ownership successor. Searchfox captures locate the corresponding upstream symbols, but are not substituted for local source: local `map_line_height_leaf` returns `Result` and computes non-length leaves through `to_computed_value`, while the indexed version uses a newer interface. Local normal-line-height conversion calls `GetNormalLineHeight`; the indexed version calls the font-metrics method directly. Local length conversion also has `in_registered_value()` branches: absolute registered lengths bypass effective zoom, and relative registered lengths undo effective zoom. Preserve that context distinction between computing the LineHeight property and computing its registered consumer. The local helper is `to_computed_value_for_math`; the indexed excerpt differs.

| Retained specified value | Inputs needed before computing it | Reading the final computed value as `lh` |
| --- | --- | --- |
| Absolute length, including an equivalent absolute-unit expression | Actual length conversion and applicable effective zoom; `resolve_line_height_length` additionally calls `maybe_zoom_text`, which reads final `_x_text_scale` | Final Length is returned directly by `ComputeLineHeight`, with the existing bridge's inflation argument of 1 |
| Plain unitless number | Its numeric computation; do not generalize this row to calc | Final Number multiplies final `aFont.size`; it does not query font metrics |
| Percentage | Converted to an `em` length against current computed font size | Final Length |
| `em` or other size-relative expression | The exact converter's current/root/inherited size basis | Usually final Length; preserve the converter's zoom rules |
| `ch`, `ex`, `cap`, `ic`, or calculations containing them | Actual current/root font metric inputs; the `ch` and `ic` orientation predicates differ | Final Length only after those metric reads have completed |
| Number calc, such as `calc(1ch / 1px)` | Visit its actual numeric AST leaves: top-level Number does not imply metric independence | Final Number still needs final size when consumed as `lh` |
| Length calc | Its actual leaf dependencies, plus the converter's percentage basis and zoom behavior | Final Length |
| `lh`/`rlh` within specified `line-height` | The converter's inherited/root line-height basis; do not substitute current-element line-height for that basis | Final Length after that conversion |
| `normal` | Computing the keyword itself is cheap | Its `lh` conversion queries the font metrics and orientation/language context |

The Gecko bridge passes no element for this registered-unit path and uses inflation 1. The resolved-value getter may pass an element instead. This report does not equate those paths or replace `aFont.size` with an arbitrary `font-size` serialization. The exact font field, effective zoom, inherited adjustment and text-scale finality must remain part of the native input certificate.

## A mask-only optimization is impossible

The actual provider returns:

```
from_unit("lh") = FONT_UNITS | LH_UNITS | FONT_METRICS | FONT_ORIENTATION
from_unit("ch") = FONT_UNITS | FONT_METRICS | FONT_ORIENTATION
```

Therefore `from_unit("lh") == from_unit("lh") | from_unit("ch")`. Even with a final literal line-height, a registered value using both `lh` and `ch` still needs the independent `ch` metric read. Removing metric/orientation bits whenever LH_UNITS is present loses that obligation. Any deterministic classifier of only this mask and the same final line-height must return the same answer for these two inputs; it cannot safely distinguish their obligations. This is a projection-information-loss argument, not a statement that the two values have equal CSS behavior.

`check_mask.py` reuses the existing provider extraction pattern and actual vendored bitflags. Two tests execute the exact frozen provider methods; two compiled false assertions reject distinct-mask and safe-global-clearing claims. Unit spelling and external enum/import scaffolding are adapted, so this does not test CSS parsing or numeric evaluation. The source methods themselves and extracted bytes are pinned; scratch is removed. No additional Lean model is needed to establish this concrete equality.

## Minimal implementable protocol

1. Retain the reached `LineHeight` declaration and its local rollback state, exact property/raw Arc, reference-walk position, and included flags. Resolve selected references through the existing resumable walk. Do not classify losing declarations, repeat substitution, or discard a Pending attr conversion. CSS-wide values and an exhausted declaration chain need the actual resulting inherited/default representation; `initial` is `normal`, not a literal fallback.
2. Separate selection/reference resolution from numeric computation. The current `resume_metric_preparation` waits for every static generated dependency before selection; `publish_prepared_metric` repeats that same test. Both gates must consume the same new value-sensitive certificate. Changing only the first leaves the deadlock; changing only the second bypasses preparation safety. Eligibility, rollback and context invalidation checks remain required.
3. Derive compute requirements from the retained specified AST and the same unit/leaf semantics as the real converter. Absolute lengths, pure numbers and percentages are classes, not a special `20px`/`30px` escape. Unsupported numeric functions or contextual leaves keep the owned continuation Pending. A classifier must not treat unknown leaves as pure. Inherit/unset/default processing preserves the native inheritance/zoom operations, then classifies the resulting representation.
4. Once the selected line-height is final, satisfy its consumer obligation by final representation: Length, Number plus finalized size, or Normal plus genuine metrics. Carry this as an LH-consumer obligation separate from direct font-metric obligations. Preserve that provenance through aliases, substituted values and typed attributes, or recover it from the retained selected AST without executing substitution twice. No mask-wide downgrade is sound.
5. Publish once through the shared ordinary/metric ownership ledger. Bind the certificate to the retained declaration, relevant input finality and unchanged context flags. Pending must preserve caller and popped-node publication state. The owned LineHeight path must avoid the ordinary full generated-dependency traversal; that existing ordinary path can remain conservative. Do not insert scheduling waits into the CSS Tarjan graph or classify a scheduling recurrence as a CSS cycle.

The next native implementation obligation is therefore a retained LineHeight action plus provenance-preserving consumer demand, not deletion of the generated LineHeight-to-Weight dependency. In the acyclic discriminator, literal line-height can become final before the selected Weight consumes registered `1lh`; direct `1ch` conversion still waits for that selected Weight and the rest of its real inputs. The current ownership successor contains early ordinary application but intentionally does not yet provide this progress path.

## Validation and limits

The existing three-case `css-registered-lh-reentry-probe-v1` distinguishes the metric target from absolute-custom and literal-weight controls. It does not cover number calc, mixed `lh + ch`, normal, inherited zoom, or all rollback forms. Those are focused follow-up cases for the implementation boundary, not observations made by this report. No running pair was read or changed.

The finite `css-selected-reference-resumption-model-v1` assumes an already-selected acyclic plan and final leaf values. It does not prove that this native classifier discovers all reads, that generated dependency order is unnecessary, or that arbitrary metric wait cycles terminate. Genuine unresolved cycles remain explicit Pending until a separate policy is chosen. This package introduces no such policy and no native refinement claim.
