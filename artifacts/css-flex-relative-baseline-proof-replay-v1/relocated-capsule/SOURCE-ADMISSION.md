# Exact source and interpretation boundary

## Versioned native target

The official relative-position repair changes two existing fallback getter calls in `PopulateReflowOutput`, independently of the natural-donor repair. `source/standalone-976279105b2e.cpp` is the authenticated standalone result. Reversing the exact two getter/format hunks reconstructs `source/upstream-original.cpp`, whose complete SHA-256 equals the original hash in the root packaging receipt. The shared `before.cpp` and `candidate.cpp` are separately retained; the shared delta additionally changes the new natural-donor helper. This third change belongs to the independent natural-donor v2 package and is not a prerequisite here.

Six complete source bindings cover original, standalone and shared `PopulateReflowOutput`, both normal-position getters, and the `LogicalPoint` constructor. The latter provider files were identified with Searchfox, then copied from the exact local files to avoid asserting indexed/local identity. Their hashes pin inspected source; they are not an independent binary-build attestation.

The extractor is a balanced-brace lexical utility for these inspected C++ forms, not a general C++ parser. Native calibration compiles the complete normal-position getter bodies and logical-point constructor, plus the exact two standalone fallback statement blocks. It does not compile full Gecko or the complete caller. Synthetic adapters supply the selected line, item array, resolved ascents, frame property store and geometry. The original logical-position getter is represented by an explicit coordinate facade; its complete native implementation is not compiled here. The caller invokes GetNormalPosition with its default null optional output pointer; calibration does not claim all nonnull-output API histories. Do not call the comparison a whole native baseline proof.

## Mathematical contract

`RelativeBaseline` models the actual presence-sensitive `NormalPositionProperty` read, including absent-property fallback to current position. Logical block coordinates distinguish horizontal-tb, vertical-lr and vertical-rl. Source first/last fallback expressions and the raw item-order reversal are separate from the independent expected-normal-coordinate reference. The selected line is supplied; line selection, collection and CSS order construction are not derived. The reference deliberately preserves the same existing donor-selection policy and independently chooses normal coordinates; it is not a proof of CSS donor-selection conformance. The natural-donor defect and scroll-container last-baseline provider defect remain separate.

The general refinement needs readiness only for a donor actually used when the incoming ascent is unset. The stronger all-items-ready corollary is convenient but not required. It preserves established ascents and empty lines. The read trace records the selected property-provider identity/presence, at most once per group; the getter's optional caller output is not asserted to be written when its pointer is null.

`visualShift` is a representation constructor: it changes actual position while storing the expected normal position and leaving dimensions, resolved ascent, identity and order unchanged. Theorems derive independence for arbitrary finite lists made this way. They do **not** prove that every native relative-position update constructs such a record. Missing and stale properties have explicit counterexamples. `PropertyReady` is a physical-coordinate/provider requirement, not an assumption that the final baseline or parent position is correct.

The original error has opposite signs in first/last group distances but the same sign after conversion to a start-relative parent baseline. The paired-parent equation assumes a common parent reference baseline and unchanged parent policy. It is not a proof of all parent flex/line-layout passes, cache invalidation or scheduling.

## Arithmetic and downstream limits

Native calibration uses bounded ordinary coordinates. Separate universal bounds cover container-minus-frame dimensions, logical-point origin subtraction, position-plus-ascent, last-group conversion and parent subtraction. The sufficient envelope bounds every executed intermediate. Native width, storage/lifetime, non-reentrancy, compiler/runtime and actual source/provider lowering remain admissions. A stricter envelope excludes the native unset sentinel; readiness alone does not exclude it, as a concrete witness shows.

The local fallback fields can still equal `nscoord_MIN`; downstream contextual synthesis then runs. A claimed final natural/public baseline therefore additionally requires a non-sentinel result and the actual downstream publication/parent contracts. The proof does not silently treat a local field assignment as delivered CSSOM/layout output.

Normal-property installation/removal and lifetime, stable normal geometry and resolved ascents under real updates, orthogonal donors, other writing modes, sticky scrolling, fragmentation/continuations, push-before-reflow readiness, and full F11/F12 remain outside this component. No hypothesis says arbitrary provider results are already correct CSS baselines.

## Normative and runtime evidence

The retained primary-section trace composes CSS Position relative-position non-descendant isolation with CSS Align baseline export and CSS Flexbox baseline selection. That restricted interpretation is independently supported by calibrated root browser evidence. The kernel checks the stated mathematical model, not the prose-to-model interpretation. Root's 288-case pair and standalone apply/reverse/commutation receipts remain separate evidence; no isolated upstream browser execution is claimed.

The fixed finite corpus includes fresh, absent and stale property states deliberately. Agreement on stale/absent states means faithful source behavior, not that those states satisfy the desired CSS observation. Only the readiness-qualified theorem claims agreement with the expected normal-coordinate reference.
