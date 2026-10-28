# Current second-endpoint guard

Source-reachable potential panic, not a browser result or severity assignment. All seven primary captures equal committed HEAD 082ab2a7d9e6576bf12e2958821d4d0e606fe620 (HEAD-JOIN.json). This route does not require the proposed Round/ModRem change.

`TimingFunction::parse_linear_function` parses output 0 followed by first percentage 0% and a second percentage calc. `CalcNode::into_percentage` checks numeric type and keeps the simplified AST. TreeCountingFunction has number type; multiplication by percent therefore has percent type. Its canonical_value is None. Product simplification requires canonical values, so the contextual tree leaf remains. Context-free `CalcNode::resolve_internal` fails on that leaf, `CalcNumeric::as_percentage` returns None, and `Percentage::resolve` / `ToPercentage::to_percentage` return None.

The guard uses `input_start.as_ref().or(input_end.as_ref())`: a present first percentage masks the second. First 0% resolves, the guard passes, the first builder insertion succeeds, and the second `to_percentage().unwrap()` receives None. Relative em divided by absolute px provides another contextual percentage when typed arithmetic is enabled: the em canonical_value is None and the product cannot become a canonical percentage without context.

The tree route checks the tree-counting preference and ParserContext::has_element_context. Normal element declaration parsing is the proposed entry; elementless API parsing must not be assumed equivalent. A literal two-position control and unresolved single-position controls distinguish grammar support from the masked endpoint. LINEAR-CASES.json is a proposal only. Do not batch suspected panic cases into the ordinary consumer probe.

A narrow guard repair would validate every supplied endpoint before any unwrap, preferably convert each endpoint once fallibly and use those resolved results. This would preserve the existing context-free admission policy; it would not implement contextual easing or justify that policy normatively. Full easing activation is a separate representation/context contract.
