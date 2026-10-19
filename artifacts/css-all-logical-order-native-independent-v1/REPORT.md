# Independent all-order native and WPT review

Date: 2026-10-19. Recommendation: accept the narrow declaration-block repair
and its WPT. The normative/discovery review is separately frozen at
css-all-logical-order-independent-v1. This report adds the expanded exact-byte
browser pair and two-file patch gate; it does not claim a universal native proof.

## Source delta and caller contract

Candidate declaration_block.rs SHA256:
`8474218db02f8787c212f47a08be33a468553b4ab809e774f2d26d4ae098812a`.
The private declaration_update body is the former ordinary map closure with only
whitespace changes. Normal batching, plan accounting and index fixups retain
their behavior. The all preparation gate now includes opposite-mapping ordering;
all execution consults the helper against the state after each preceding update.

None skips, UpdateInPlace sets value and importance, AppendAndRemove removes the
aligned vector and importance entries before insertion, and Append inserts
identity/value/importance. This preserves the intended unique-ID representation
at return, under its existing canonical-input premise. The temporary retained
ID bit during remove/reinsert is internal; no new callback appears in that loop.
All expansion remains lazy and pref filtered, excludes direction/unicode-bidi/
custom properties, and never enters the ordinary bounded shorthand buffer.
The CSSOM caller creates a fresh plan and invokes its pre-change callback once.
Stable metadata and no intervening mutation remain source/caller premises.

The initial any(non-None) gate is equivalent to existence of a changing
sequential step by the first-change argument in the discovery review. It is not
equivalent to final cssText inequality. Repeated identical all can temporarily
reorder then restore the final list and still report changed. CSSOM permits this;
this review makes no no-mutation-event assertion. Using parsing push would be
incorrect because it refuses normal-over-important replacement.

The patch does not add a new input parser or change property values. It can add
vector shifts and call the decision helper sequentially for all; no performance
measurement or universal allocation/complexity proof is claimed. Root's build
and the concrete native logic provide the implementation evidence here.

## Independent WPT oracle review

The 40 subtests combine four values (initial/inherit/revert/var(--all)), two
priorities and five families. Fresh all expansion calibrates relative physical/
logical pair order without imposing an absolute canonical order. The open
CSSWG canonical-order discussion is retained in the discovery report; same
shorthand/provider context must have a stable expansion for this relational
oracle. This is a CSSOM item/order observation, not a rendering oracle.

The equal-value family deliberately moves the first calibrated pair member
after the other, asserts that perturbation, then repeats all with identical
value and priority. It directly catches the formerly false no-change gate.
The priority/exclusion family reverses old/new priority and checks both
longhands, direction, unicode-bidi and a custom property, plus identity
uniqueness. Longhand and cssText controls remain independent of the repaired
special all execution branch. The test uses detached ordinary elements and
requires no asynchronous resource or font timing.

Every passing candidate all subtest executes both seed orders. Each failing
baseline all-expansion subtest stops at the first seed; the equal-value family
separately reaches its final assertion after its perturbation succeeds. We do
not infer unexecuted baseline assertions. The test does not exhaust every
logical group, all keyword, computed value or generated property configuration.

## Exact paired evidence

Independent parsing of the raw JSONL yields 105 unique action/test/subtest keys.
Baseline: 85 PASS, 16 FAIL, four OK. Candidate: 101 PASS, four OK. The sixteen
changes are exactly eight all-expansion and eight equal-value cases, all
FAIL→PASS. The other 89 normalized outcomes are identical. All 40 new subtests
pass, and 61 existing subtests pass unchanged. Existing files are logical setter,
cssText and the earlier link-parameters publication regression. No additional
unrun all-shorthand serialization test is represented as passing here.

Input/before/after pins are stable in each phase. Fixed pins differ only at
native declaration_block.rs; served WPT/config/other source hashes match.
Both binary hashes differ after the forced Rust rebuild and link; build-after
binaries equal candidate browser input. Both commands return zero. The link log
retains four build-monitor KeyError/export traces despite successful linking;
we make no warning-free build assertion. Candidate harness exit and WPT lint
are zero. The whole native file is stable under root's rustfmt2024 check.
This is a shared macOS project build, not isolated upstream runtime.

## Standalone patch and acceptance boundary

The two-file native/WPT patch hash is
`e2a185b68d6a3ad483ebce3f9cc77268bc6684d70ad406d40db4ef5e8466db3c`.
This reviewer independently applies/reverses it only in a temporary artifact
copy and compares full resulting source and HTML bytes. Root's separate
STANDALONE-CHECK records the same patch applying/reversing against upstream
976279105b2e78b8666a959eb3f25c9176cefaf8. That Git check is retained root evidence,
not repeated independently here. No isolated upstream build was run.

No native/WPT acceptance blocker was found. The planned state-dependent
planner/executor formal companion remains separate. The prior declaration
publication proof over independent actions does not supply that missing native
lifecycle theorem. No discovery history or original broader obligations are
rewritten by this narrow acceptance recommendation.

## Replay and roster

After authenticating the review freeze, run `python3 -I -S check.py`. It verifies
its closed files and the exact sibling discovery/browser capsules, reconstructs
all raw identities independently, checks build/source/test bindings and applies
and reverses only an artifact copy. It imports no producer helpers and runs no
Git, browser or compiler. COMMIT-INVENTORY.json lists all source-only companion
files and the two repair files; temporary build outputs are excluded.
