# Successful typed output discarded by an enclosing grammar

Status: source-backed probe, not browser-confirmed and not a native proposal. Same random-index rollback family, no additional accepted bug count.

`grid::parse_value` first tries `grid_template::parse_grid_template` inside cssparser `try_parse`. In its ordinary track-list branch, the latter successfully creates `template_rows`, consumes `/`, then parses columns. For `random(property-index-scoped, 10px, 20px) / auto-flow 100px`, the row LengthPercentage and TrackSize succeed; `auto-flow` is not a template column track. The enclosing call returns Err and drops its owned row AST. No returned value retains this failed attempt. The fallback parses rows again, followed by the accepted auto-flow grammar. Token rollback does not roll back PropertyDeclarationContext.random_count.

The seven typed-finalizer transactions do not repair this path: the first row's typed parser returns Ok, so its index increment is intentionally retained. A transaction must surround the speculative whole grid-template attempt, including its later column failure. The subsequent row-prefix trial is another compound attempt worth auditing; no global closure is claimed. A counter-only wrapper around the existing first try_parse would be a bounded repair candidate, subject to actual evidence and review.

The one-row source prediction is index2 rather than1. Two random row tracks predict indexes3/4 rather than1/2. A row and auto-column random predicts2/3 rather than1/2. Explicit-template, auto-flow-first, named and fixed controls should match their same-key references. Distinct random samples may coincide; specified key serialization is retained independently of computed output.

observe.js is a standalone async function with seven rows and four expressions per row, owned iframe cleanup, support checks and specified/computed longhand snapshots. It installs no native code. Root owns execution. Syntax check2a3b3b/0; no browser executed by author.

Source capture: shorthands.rs is the exact previously sealed current/upstream-equal capture from css-random-speculation-boundary-audit-v1. Fresh Searchfox grid.rs capture a95e9d/0 is paired with current grid.rs; GRID-LOCAL-DELTA.patch explicitly retains branch differences. The TrackBreadth→LengthPercentage and TrackSize success route is present in both; do not claim whole grid.rs equality. Searchfox identifier query00353a/0 confirmed entry points; unsupported --permalink option22dbef/2 was not used as evidence.
