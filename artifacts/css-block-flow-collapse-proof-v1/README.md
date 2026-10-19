# Collapse-through classification and signed-margin traversal

This companion models the reviewed local guard in
nsBlockReflowContext::ComputeCollapsedBStartMargin. It does not verify all reflow,
the implementation of IsSelfEmpty, CSS parsing, or arbitrary fragmentation.
The formal and native evidence are separate and replayable.

## Replay

From the checkout root:

```sh
python3 artifacts/css-block-flow-collapse-proof-v1/check.py \
  --out artifacts/css-block-flow-collapse-proof-v1/replay-local \
  > artifacts/css-block-flow-collapse-proof-v1/replay-local.stdout.log 2>&1
```

The output directory must not exist. SOURCE-v1.json pins tooling, retained inputs
and current native source identities. TOOLCHAIN-v1.json pins the actual Lean and
Clang executable paths and hashes. The checker rejects compiler warnings/errors,
unexpected Lean output, unsupported axioms, runtime diagnostics, incomplete
output, source drift, and undetected negative controls. A source-only tooling
list excludes generated executables, scratch files and replay logs. Root owns
native changes, builds, browser runs, commits and independent review.

## Lean model

Collapse.lean imports Std and audits 34 named theorems. It uses signed integer
pairs `(maximum nonnegative margin, minimum nonpositive margin)`. The collapsed
value is their sum. Joining pairs is associative, commutative and idempotent;
aggregation over arbitrary finite edge lists preserves those bounds, distributes
over concatenation, ignores duplicate entire traces, and is invariant under
swapping chunks. Reducing every intermediate pair to a single scalar is wrong:
10 and -8 yield2, but subsequently adding5 must retain2, not produce5.

The endpoint witness is `max(0,min(basis,1000-basis))`, exactly ten times the
pixel-valued expression `max(0px,min(10%,100px - 10%))` at integral pixel bases.
It is zero at0 and1073741823, positive at100. This is a mathematical rational
counterexample to inference from two endpoints, not a theorem about the CSS
parser, floating-point evaluation, app-unit rounding or overflow.

Dimensions contain optional natural preferred/minimum sizes and nonnegative
logical start/end border-padding. None is unknown, never a huge positive length.
The native ordinary maximum1073741822 is distinct from the exact unknown
sentinel1073741823. Refinement preserves old nonempty answers, preserves hidden
answers, preserves zero/unknown dimensions, and rejects nonhidden positive
separation. These are supplied whole-element resolved content-box constraints,
not assertions about remaining fragment extent.

The recursive Tree/Forest model covers ordinary finite normal-line trees. Each
node has supplied old self/fallback eligibility, hidden/margin-root flags and
resolved dimensions. Forest nodes distinguish a child block, an empty/nonempty
inline line, and an explicit clearance tag; a zero-valued clearance tag stops
traversal. Traversal records each margin's start/end identity before aggregation.
Both original and revised models are defined on the same tree and inputs.

The guard executes after a block's start and eligible descendant starts have
been collected. The compositional theorems lift positive separation through
visit: a nonhidden separating frame reports nonempty, its caller retains its
collected starts, and neither its own end nor following siblings are admitted.
The 10/20/80 witness checks exact edge membership and the80→10 collapsed values.
A positive parent with a child start40 proves that an early return would lose a
legitimate contribution. A start-padding or formatting-root barrier instead
uses the explicitly supplied fallback eligibility.

The universal model intentionally has no overflow/next-in-flow lists. Native
output initialization can retain an earlier true result after a later fragment
stops traversal. A true slot therefore is not proved equivalent to structural
emptiness of every fragment. The model's sibling theorem uses the child's
reported eligibility, and its all-input claims apply only to the stated finite
normal-tree representation with supplied providers.

All theorem dependencies are printed. Only the standard Lean axioms propext,
Quot.sound and Classical.choice are allowed; the exact set per theorem is in
the receipt. No sorry/admit/unsafe or introduced axiom declaration is accepted.

## Exact native bridge

bridge.py extracts the complete original and candidate
ComputeCollapsedBStartMargin definitions without modifying their bodies. The
candidate whole file must equal the original with precisely guard.txt inserted;
all other function and caller bytes are preserved. The complete exact
CollapsingMargin class is extracted from ReflowOutput.h, and nscoord_MAX plus
NS_UNCONSTRAINEDSIZE declarations are extracted from their pinned headers.
Compilation uses C++20, warnings as errors, undefined-behavior and integer-
truncation sanitizers, and no sanitizer recovery.

The adapters provide frames, logical margins, ReflowInput sizes, style flags,
wrapper descent, normal/overflow lines and next-in-flow chains. They do not
reimplement or prove Gecko's layout size providers or physical writing-mode
conversion. Logical inputs are already resolved in one compatible coordinate
system. DescendIntoBlockLevelFrame is supplied by a single explicit wrapper
link, with the native parent assertion preserved. Input graphs are finite and
acyclic; fixture coordinate sums remain representable.

The native output includes collapsed value, both retained signed extrema,
IsZero, the output slot, retry/dirty return, ReflowInput construction/destruction
counts, each line's clearance flag and dirty-mark count, and a trace of margin
start/end reads, line visits, and self/fallback emptiness calls. The exact
CollapsingMargin scalar Include path is exercised; its summary Include overload
is compiled but is not claimed separately executed by this traversal.

The independently written Python reference collects margins and effects over
segments. It explicitly retains whether the output was initialized after the
first normal pass. Empty normal lines followed by nonempty overflow or next-flow
lines can stop traversal while retaining the earlier true result. The output is
not reset to a recursively invented all-fragments-empty predicate. An absent
output pointer leaves the caller's initialized slot unchanged. Hidden input
preserves an old true result; it does not force a prior false result true.

The 2,180 finite fixtures cover:

| Domain | Cases |
| --- | ---: |
| Supplied size/hidden/old eligibility/block/root/output classification | 1,536 |
| Ordinary sibling start/end membership with signed margins | 480 |
| Late guard with legitimate nested start contribution | 6 |
| Inline emptiness, stale clearance tags and retry initialization | 16 |
| Normal/overflow/next-flow output initialization and stopping | 96 |
| Wrapper descent, root/fallback and no-output cases | 32 |
| Distinct self-empty versus fallback-empty providers | 8 |
| Recursive dirty and clearance propagation | 2 |
| Descending signed extrema retention | 4 |

For 1,266 ordinary-tree fixtures, generated Lean expressions execute both models
(2,532 evaluations). Their margin extrema, collapsed value, through result and
ordered edge identities must agree with the independent Python oracle and both
compiled native capsules. This is finite source/model correspondence evidence,
not a compiler correctness or universal compiled-C++ theorem.

## Negative controls and provenance

Semantic controls corrupt signed extrema, unknown handling, minimum/start/end
padding, hidden exemption, sibling admission, early-return placement, output
initialization, overflow/next-flow traversal, clearance, retry and dirty effects.
Lean controls additionally corrupt the explicit zero-clearance tag. Diagnostic
and per-input identity mutations must be rejected. Whole-file preservation
controls change unrelated file content, clearance/sibling logic or the guard.

The first preflight exposed an insufficient test sequence: a positive-margin
overwrite mutation survived because subsequent larger margins restored the
maximum. Four descending signed sequences were added and are also evaluated
through both Lean models. The failed preflight remains retained separately;
it is not a passing receipt and does not belong in the source-only tooling list.

Retained PROOF-PLAN, DESIGN, independent native/proof-plan reviews and root
boundary review establish the intended scope and its corrections. Paired
boundary receipts are identified in PROVENANCE-v1.json rather than required as
external runtime dependencies:28 cases/84 states per mode,10 normative
differences→0,80 fragmented geometry components→0, no literal changes. The
native WPT and provider/fragment browser results support finite observations;
they do not supply unproved universal assumptions to Lean. This author prepared
the boundary fixture and companion; final independent review must be by another
agent. This companion changes no native source, WPT, build or browser state.
