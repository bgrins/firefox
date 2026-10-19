# Native prediction and prior art

All complete local files used below are retained in `source/` and pinned by INPUTS.json. The corrected A+B+D then C cascade snapshot is used; this hypothesis does not depend on rollback.

1. `DeclarationIterator::update_for_node` obtains a reversed importance-filtered declaration iterator. `iter_declarations` calls `maybe_note_non_custom_dependency` for non-custom `WithVariables` declarations carrying ATTR references before applying the longhands.
2. `SubstitutionFunctionReference` retains the local name in `name` and the resolved namespace separately in `attribute_data.namespace`.
3. `Cascade::update_attributes_map` admits typed references using `seen.custom.attr.insert(&next.name)`. A prior reference with the same local name blocks preload even when the namespace differs.
4. `get_attr_value_for_cycle_resolution` correctly queries the namespace of the first admitted reference. `ComputedSubstitutionFunctions::insert_attr` stores the result in an `OwnMap` indexed by the local name only.
5. The Attr substitution branch queries the correct namespace again, but for Type outside container queries replaces that value using `substitution_functions.get_attr(&reference.name)`. Both namespaced references therefore receive the first preloaded local-name value.
6. Source prediction: the width-then-height case reads b:x first and produces 37px/37px; reversed declaration order reads a:x first and produces 13px/13px. Browser execution has not occurred in this package.

The six controls distinguish each namespace alone, distinct local names, identical qualified names, the numeric-unit path (which bypasses the typed lookup), and null/named namespaces with distinct local names. DOM namespace/value readback, declaration CSSOM, syntax support, namespace-rule count and a 100px containing block are retained by the probe.

## Prior art

Bug 2021110, `[css-attr] Chained references should support namespaced attributes`, remains NEW in the fresh Bugzilla response retained in BUG-2021110.md. The source TODO in `get_attr_value_for_cycle_resolution` cites that bug when parsing nested references with no namespace map. Bug 2021110 comment 1 calls for namespaced attribute infrastructure during cycle detection and substitution.

This witness contains no chained reference or custom property: its two direct literal attribute values collide before nested parsing matters. That narrows the reproduction but does not establish a distinct or novel bug. Treat bug 2021110 as potentially covering the same representation deficiency; root should adjudicate duplication before filing or assigning a new identity.

No universal proof or accepted native defect is claimed from this source trace alone. The postguard observer algebra keeps attribute identity as (local name, namespace), so it does not justify this name-only substitution map.
