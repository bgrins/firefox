# Discovery log

2026-10-19 Searchfox queries: `--path testing/web-platform -q escaped-eof`; `--path servo/components/style -q 'impl ToCss for SpecifiedValue'`; `--path servo -q Servo_DeclarationBlock_GetPropertyValue`; `--path layout/style -q 'Servo_DeclarationBlock_GetPropertyValue('`; `--path servo/components/style -q 'pub fn property_value_to_css'`; `--path servo/components/style/properties -q PropertyDeclaration::Custom`; `--path servo/components/style/properties/properties.mako.rs -q 'pub fn to_css'`; `--path third_party/rust/cssparser/src/tokenizer.rs -q 'fn consume_unquoted_url'`.

Initial searches failed DNS, later searches returned the exact pinned paths. Local complete-file reads followed discovery. No source revision identity inferred from Searchfox index.

Bounded prior-art queries: `"escaped-eof.html" Firefox`, `"custom properties" "escaped" "EOF" serialization`, `site:github.com/w3c/csswg-drafts "EOF" "custom" serialization`, `site:bugzilla.mozilla.org "escaped EOF"`.

Relevant reporting records:

- https://bugzilla.mozilla.org/show_bug.cgi?id=1611178
- https://bugzilla.mozilla.org/show_bug.cgi?id=2050643
- https://bugzilla.mozilla.org/show_bug.cgi?id=2082681

The bug 2050643 direct page fetch failed; search extracts identify its WPT-sync title and affected tests. No dedicated defect adjudication was inferred from these records.
