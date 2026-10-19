# Discovery record

Searchfox CLI was used before local caller reads. The recorded batch in DISCOVERY.json failed DNS; individual retries succeeded. This file records observations, not a raw successful response.

- `searchfox-cli --path third_party/rust/cssparser -q parse_nested_block -l 12` found the public wrapper and provider in parser.rs.
- `searchfox-cli --path servo/components/style -q parse_qualified -l 12` located the inline declaration and stylesheet nested-rule providers.
- `searchfox-cli --path servo/components/style -q NonNegativeLengthPercentage -l 12` found padding-left's type declaration in longhands.toml.
- Earlier `set_nested_block_limit` query under servo returned zero results.
- `searchfox-cli --path testing/web-platform/tests/css -q 'nested calc' -l 8` returned calc-nesting.html, calc-nesting-002.html and calc-serialize.html. These test valid math; no exact recovery-limit test was established.

No Searchfox revision is substituted for retained local source identity. Local syntax WPT/metadata filename survey found invalid-nested-rules.html and no depth/limit-named test; this bounded filename check is not exhaustive or execution evidence.
