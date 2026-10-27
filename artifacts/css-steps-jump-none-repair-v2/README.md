# Context-free calculated jump-none counts

Four-path uncompiled proposal: one Rust source, two existing WPTs, one new WPT. Exact PREIMAGES/POSTIMAGES and gecko-wpt.patch are supplied. No live source, test, metadata, index, canonical or ledger was edited; no browser or build ran.

The parser still rejects calculations that cannot resolve without context. Literal jump-none one is rejected using Integer::get(); positive-integer parsing continues to reject literal zero/negative values. Only boxed calculations receive the jump-none minimum of two in the existing shared conversion. Other step positions, cubic-bezier/linear code and ToComputedValue delegation remain unchanged. This is not the contextual steps admission/retained-keyframes proposal.

Source coupling: exact committed preimages were read from 19a313060adbaf6e4817df03bcb965302dff9ef9. The implementation uses the already accepted/committed fix121 Integer::resolve positive stored-range behavior and Integer::get literal-versus-boxed distinction. It does not require held120 or the unaccepted contextual steps prototypes. Root must verify these source preimages against the intended current restored checkout before applying; no clean-old-HEAD independence is claimed. Readonly easing tests are frozen separately.

The explicit NaN oracle correction changes an invalid-value test to a valid specified-value test expecting steps(calc(NaN), jump-none), and adds a computed-value test expecting steps(2, jump-none). This is a test correction supported by trace-v2, not an expected-failure metadata waiver. No metadata is changed. Historical raw remains untouched and is pinned in REFERENCES; a local copy of its 76 subtest records is retained. Its process cleanup/terminal authority is not inferred here.

The new fixture retains the historical 18 test names. Two getter assertions were corrected before landing: getTiming() returns specified timing properties, and non-CSS getKeyframes() returns source keyframes with computed offsets, not generally computed property/easing values. Neither getter is asserted to equal a computed two-step string. Their strings must remain valid easing serializations; actual targetless progress and keyframe output independently check the two-step result. Literal getter calibration remains exact. See SERIALIZATION.md.

Run all four CONFIG tests on original, candidate and restored native sources with the same proposed WPT bodies. The new roster is 77 (old 76, one renamed NaN syntax identity and one added computed NaN identity). Candidate requires 22 focused PASS cases and the other 55 historical controls unchanged, including five unrelated failures. Restoration must match the fresh original 77-case capture exactly. No fresh baseline/candidate/restored result is prefilled. Do not claim the earlier original fixture's unreachable getter assertions were observed.

Validation: scoped rustfmt with edition2024 and servo/rustfmt.toml passes; earlier edition2021 checks are retained and reported import ordering differences, not candidate formatting changes. Node syntax and inert registration checks pass for all four files. Filesystem-only apply/reverse reproduces exact pre/post maps. WPT lint import was unavailable in the default Python environment (missing yaml); no dependencies installed or browser lint surrogate claimed. Native compilation and WPT execution remain root-owned prerequisites.

Replay static checks using an absent output directory:

    python3 -I -S -B artifacts/css-steps-jump-none-repair-v2/check.py --output /private/tmp/steps-review-UNUSED

The checker executes no test callbacks and creates/removes only its own transport scratch. It does not activate the proposal. No accepted fix number or new bug credit.

V2 changes only three sample times from 750ms to 600ms (duration1000ms). Jump-none count2 outputs1 at0.6; counts3/4 produce smaller outputs, so the numerical oracle now distinguishes them. All18 test names,77-case roster, native bytes and other WPT bodies are unchanged. Copied v1 validation logs remain historical; replay-v2 records the successor static run. No fresh browser baseline has been run.
