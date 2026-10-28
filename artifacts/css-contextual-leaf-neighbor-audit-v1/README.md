# Contextual-leaf neighbor audit

Searchfox identifier search for resolve_map in servo/components/style returned four occurrences: the generic helper/resolve adapter, computed length-percentage resolution, and the affected line-height mapper. A second bounded search for leaf.clone(), RandomKey and TreeCounting found no additional silent contextual-leaf clone in the returned specified/computed value sites.

The clone in specified CalcNode::to_computed_value is an error-propagation placeholder: failed conversion sets failed, and the function returns Err before exposing the mapped result. The clone in computed CalcLengthPercentage::resolve retains an already-computed leaf while replacing percentages with lengths. Its specified-to-computed conversion explicitly handles both RandomKey and TreeCountingFunction. These inspected sites do not exhibit the line-height mapper's unresolved-context cloning pattern.

This is a bounded source audit, not an exhaustive visitor proof or new bug. Captures are Searchfox responses from 2026-10-28; indexing may lag this checkout. No local native change, browser run, formal coverage increment or accepted fix results from this audit. Other missing context paths or different invariants remain possible.
