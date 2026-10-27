# Used bare/unit attribute fallback repair proposal

This three-path patch repairs missing cycle edges for used fallbacks on non-type attr() occurrences at ordinary custom/non-custom property nodes. It is based on committed HEAD 87445004c1ae44d9c1e2873b91f01414cf75cbb2 and does not depend on the live typed-demand prototype. No native/live-WPT application, build, browser run, index/HEAD change or accepted-fix claim has occurred.

## Change

visit_value_references currently skips these occurrences before looking at their fallback. The patch checks the primary through AttributeData::non_type_primary_is_valid and queues fallback.references only when that primary fails. It retains the existing can_chain condition, including its parent-attribute exception; the separate raw-nested oracle problem is not changed.

The classifier reads the actual expanded attribute name through AttributeTracker. A present raw/bare attribute, including empty text, succeeds. Missing/unknown namespaces and invalid numeric inputs fail. It never uses typed-provider cache membership to decide raw/unit validity.

parse_attr_number is extracted from substitute_one_reference and shared with this classifier. It preserves the existing whitespace skip, number-token parse, slice capture before exhaustion, and final exhaustion check. Its borrowed slice preserves the original token text without allocating for classification; unit serialization remains in substitute_one_reference. The parser/slice lifetime signatures were checked with Searchfox. No raw-content substitution or eager traversal of unused fallback references is introduced.

This version preserves v1 Rust postimages exactly and adds the independent reviewer's four NonCustom-root cases (34 total tests). v1 remains immutable historical evidence. The committed base revision is unchanged even if HEAD advances through research-only commits.

The captured local tree contains unrelated typed-demand work. base-live and candidate-live preserve it byte-for-byte outside these exact hunks. SOURCE-PINS.json records both committed and live preimages and their candidate postimages. The original used-fallback audit distinguishes this bug from 7822bb6's typed preparation and e3ba54f's type()-specific fallback eligibility. Both release and branch observed seven failures and six passing controls before this proposal.

## Files and transport

- fix-head.patch: complete proposed commit, two Rust files plus one WPT.
- fix-live.patch: equivalent full diff against the captured live preimages.
- native-head.patch / native-live.patch: native-only views for review.
- base-head / candidate-head: committed preimages and proposed postimages.
- base-live / candidate-live: current-tree equivalents, including unrelated existing edits.
- verify_transport.py: independently rerunnable application/reversal check in fresh owned /private/tmp directories; never uses the live tree or index as its destination.

```sh
python3 -I -S -B artifacts/css-attr-non-type-fallback-repair-v2/verify_transport.py
```

The exact fix-head.patch applies cleanly to both captured bases, yields the corresponding candidate bytes, reverses to each original byte sequence and reapplies identically. All ten git apply/check operations exited 0. Both scratch directories were removed. This includes exact three-file candidate inventories; reversing removes only the newly added candidate WPT.

## WPT and validation

The candidate attr-non-type-used-fallback-cycle.html contains 28 fixed cases, two attribute-mutation tests, and four NonCustom-root font-size/line-height cases. Its first 13 data cases match the release/branch probe exactly. Extra cases distinguish empty raw values from empty numeric values, whitespace, extra/dimension tokens, explicit/null/unknown namespaces, occurrence-specific syntax, literal function text and mutation between valid/missing/invalid primary states. Both mutual-cycle participants and the consuming color are checked.

Python and JavaScript syntax checks passed. rustfmt parsed all four copied Rust postimages successfully; the added helper and method match rustfmt output exactly. These checks are not Rust type checking or browser verification. The patch has not been compiled or tested against the WPT runner.

REGRESSION-ROSTER.json pins the existing tests and explains each gate: typed preparation/eligibility, numeric tokens, attr-cycle with its order regression and unchanged disputed raw oracle, non-custom cycles, namespace variants and bare attr fallback behavior. The parent should perform an original/candidate comparison using the exact source-pinned proposal. Expect the original seven reduced failures to pass after the fix, retain all controls, and investigate any additional-case failures before acceptance.

Only the native files and WPT belong in the eventual standalone bugfix commit. This artifact's tools, snapshots and documentation are separate research material. The raw-nested follow-up can reuse primary classification, but its existing WPT conflict requires explicit adjudication first.
