# Atan2 relative-unit folding: experimental repair, held for consumers

The source/spec chain and root's preliminary Firefox158 observations support a real zero-basis defect. This one-line native delta is an incomplete experimental repair, not an independently landable fix. It must remain held until deferred integer consumers preserve previously admitted valid declarations.

## Causal chain and primary semantics

The generic Atan2 simplifier extracts coefficients from same-unit leaves and immediately builds an angle. With equal positive em operands it produces45deg before the font basis is available. CSS Values4's [argument-range table](https://drafts.csswg.org/css-values-4/#trig-infinities) instead gives0deg for two positive zeros; [simplification](https://drafts.csswg.org/css-values-4/#calc-simplification) requires enough information to perform the operation; [computed-value evaluation](https://drafts.csswg.org/css-values-4/#calc-computed-value) supplies the em basis. Treating the expression as a symbolic ratio cannot bypass the defined zero case. Positive-basis homogeneity does not justify folding for all valid fonts.

Root's isolated MCP Firefox158 run reported all four quadrants differing at zero, all eight nonzero snapshots matching, and all twelve literal/resolved-pixel controls matching. Relative specified-style serialization already contained constant angles. The separate integer-consumer probe admitted all nine expressions and showed the three em consumers remaining3 at zero instead of1; all other snapshots matched. These are preliminary release-session observations, not independently attested stock-profile/BuildID or native-candidate comparisons. No new accepted fix number is assigned.

## Minimal local operation change

native.patch replaces the two `unitless_value` accesses in the same-unit Atan2 branch with `canonical_value`. The captured specified leaf implementation returns None for contextual lengths and hinted percentages; the tree therefore survives until real context can resolve those inputs. Ordinary independent operands still fold. Existing Angle::to_computed_value resolves CalcNumeric with an actual Context, so the transform route has a suitable continuation. This is source analysis, not a typechecked or executed candidate.

Preserve actual conversion ordering: negative zero and nonfinite results are observable inputs to atan2. Positive finite common scaling is only a sufficient mathematical intuition when intermediate rounding/underflow does not alter the operands. Do not replace resolved operands with their ratios or rescale them to1 before evaluation. Infinity times a zero relative basis can generate NaN; nested NaN preservation/outer censorship needs independent evaluation against the existing raw-length work. The finite zero-font fixture does not certify all those cases.

## Required consumer completion

`calc(1 + 2 * atan2(1em, 1em) / 45deg)` has a valid positive integer result:3 at a positive font and1 at zero. With the current coefficient fold it is context-free3. With this delta it becomes contextual. Existing steps() and subgrid name-repeat parsers call Integer::resolve without Context and reject None; deleting those guards would expose their later context-free unwrap/cache/export assumptions. This is the same documented dependency as held120 and the previously captured bug2037743/bug2037744 workstreams. It is not a new parser-crash claim or a reason to preserve incorrect folding.

The complete repair must carry specified Integer through the easing and subgrid representations, perform property-appropriate positive/range handling at computed-value time, and derive every count/cache/export from that computed value. Easing's animation/keyframe/FFI boundaries and subgrid's allocation/expanded-name bounds must be updated consistently. Support valid deferred counts without relaxing structural grammar or allowing unbounded allocation. A Context-free site must retain a principled rejection or explicit demand; it must not substitute a guessed count. The next implementation task is this concrete prerequisite, not acceptance of native.patch alone.

## Test and validation scope

atan2-relative-zero.html is an unexecuted14-case WPT draft: eight quadrant/offset transform cases and six em/px integer-consumer cases. Each captures all three mutation states before assertions. Literal and resolved-pixel controls calibrate transforms; literal count references calibrate steps, subgrid, and z-index. The two em steps/subgrid cases deliberately remain in the acceptance set to expose the predicted admission regression. No failing case was removed to make the narrow patch appear complete.

Static JS parsing and fourteen unique callback registrations passed d92185/0; callbacks were not executed. Exact forward/reverse/reapply patch transport passed1b4acc/0 in removed private scratch. Rustfmt parses both bodies, and their formatted delta is exactly the intended Atan2 change. Whole-file rustfmt --check1fa149/1 reports preexisting import ordering and Random-node layout differences; no unrelated formatting churn was added. No build, native test, browser candidate run, canonical WPT installation, or live source/index/epoch mutation occurred.

The native base is an authenticated local branch capture, not a claim of pristine-upstream equivalence. Four finite-quadrant Lean laws are separately checked; their signed-unit table is a manual abstraction and does not refine Rust floats, trig, parser admission, or all CSS units.
