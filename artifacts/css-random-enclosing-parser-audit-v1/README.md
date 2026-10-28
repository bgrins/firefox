# Additional enclosing-parser audit

No new accepted-declaration counterexample was established in this bounded source audit. The confirmed grid-template rollback issue remains the actionable enclosing-parser case; this report neither closes the parser family nor adds a bug or validation count.

Four current Searchfox source bodies were captured and independently compared byte for byte with the corresponding local files: specified position, specified transform, specified image, and property shorthands. All four match. SOURCE-PINS.json authenticates both copies. The fetches followed Searchfox discovery and used its `--get-file` command; the fetched main-branch bodies have content hashes but no independently captured immutable upstream revision. This is not a claim about a stock browser build.

## Findings

| Audited boundary | Concrete source result | Observable witness status |
| --- | --- | --- |
| `flex::parse_flexibility` | Once mandatory grow parsing succeeds, optional shrink failure is swallowed and the helper returns success. It does not later discard a successful grow through its own `Err`. | NOT REACHED for the proposed outer-failure mechanism in this helper. This does not cover every flex-basis parser. |
| `border_image::parse_value` width/outset closure | The enclosing slash closure returns `Err` only when both width and outset are absent. A successful width prevents that outer failure. | No new accepted retry established. The internal width/outset grammars were not exhaustively audited. |
| `background::parse_value` position/size trials | A failed optional slash-size trial restores the slash; no inspected background alternative accepts that slash as an unrelated item. A discarded successful size prefix therefore does not alone establish an accepted declaration. | NOT REACHED for this attempted route; no exhaustive image/background claim. |
| `Position::parse_three_value_quirky` vertical-first lookahead | After `top`, the `lp_and_x_pos` trial can successfully parse a random length, then fail because neither a horizontal keyword nor `center` follows. The trial restores tokens, but the external count is not rolled back here. The method returns center/top and leaves the random token. | The internal discarded-success path is REACHED by source reasoning. A new valid outer-declaration witness is NOT ESTABLISHED. |
| `TransformOrigin::parse` | It has its own `OriginComponent` algorithm rather than calling the preceding Position parser. Its successful first-component route consumes optional second/depth components without that mandatory post-length horizontal-keyword check. | The tempting `transform-origin: top random(...)` attribution to the Position leak is NOT REACHED. |
| `EndingShape::parse` explicit ellipse pair | The pair trial can successfully parse the first radius, fail the second, restore both tokens and return the default ellipse extent. The first radius's random count can survive that failure. | Internal discarded-success path REACHED by source reasoning; no valid gradient accepting the remaining radius was established. |
| Modern/legacy radial and conic gradient prelude callers | The inspected paths require a comma after a recognized prelude. The numeric token left by the preceding failed trial prevents that delimiter from being consumed. The numeric function is not thereby converted into a valid color stop. | No new accepted gradient witness established. No claim about every image branch. |
| `offset::parse_value` | Distance and rotation are only parsed when an offset-path was accepted. The attempted position-only `top random(length)` route leaves the numeric token and supplies no path. | NOT REACHED for that attempted accepted shorthand. Other motion/basic-shape internals remain outside this audit. |

## Why the internal paths are insufficient

Using `R = random(property-index-scoped, 10px, 20px)`, the Position trial for `top R` can consume R speculatively and then return only center/top after its horizontal-keyword check fails. Similarly, the shape trial for `ellipse R` can discard R after a missing second radius. These are useful source-level transaction boundaries, but neither token sequence is a demonstrated accepted declaration in the inspected callers. Counting them as two new observable bugs would confuse a parser-state side effect with a successful alternative whose computed value exposes it.

No browser probe is supplied for these incomplete witnesses. A useful next experiment requires a caller that legally consumes the restored numeric token in a different role, or an additional alternative that succeeds after the complete first branch fails. The confirmed grid case satisfies that stronger condition; the examples above currently do not.

## Existing work and limits

The predecessor `css-random-caller-transaction-audit-v1` already identifies the whole grid-template trial: successful row ASTs are discarded when the later column grammar rejects `auto-flow`, then the grid shorthand legally reparses the same rows. That source prediction was subsequently observed with shifts 1, 2 and 1. The current four-source proposal wraps that entire trial, registered syntax alternatives, and seven typed finalizers. It must not be described as a general transaction around every speculative CSS parse.

Typed finalizer rejection is distinct from these enclosing trials: successful finalizers retain their increments intentionally. This audit does not propose resetting successful component parses, resetting a counter to zero, or changing CSS parsing order. It does not audit non-counter side effects or prove every discarded AST is harmless.

The basic-shape Searchfox query is recorded as discovery only; those implementations were not captured or fully traced. No native source, index, runtime epoch, build output, test fixture or browser was changed. Only this new artifact directory was written.
