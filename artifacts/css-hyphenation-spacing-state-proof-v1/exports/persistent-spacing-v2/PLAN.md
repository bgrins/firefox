# Persistent spacing state: continuation plan

Original full ownership obligations are unchanged. This supplement targets the missing association between successive native CalcTabWidths queries and the previously proved local tab calculation.

1. Bind the complete native constructors, GetSpacing/GetSpacingInternal, CalcTabWidths, TabWidthStore and EnsureTextRun property invalidation. Record reflow versus non-reflow/intrinsic branches, frame/run/start and property ownership. Do not assume InitializeForDisplay/Measure or SetStartOfLine are inert; their timing is a caller premise until traced.
2. Prove an independent prefix reference for one persistent reflow provider: from its constructor state, arbitrary query ends cover exactly the maximum requested prefix; old prefix numeric values/cache entries are retained, newly requested indices are processed once in source order, and full value operation order is preserved. No global floating-point reassociation is used.
3. Thread the returned state through spacing request histories. Include no-calculation, intrinsic return, saved-property load and property publish/remove effects; distinguish a single stable provider from changes of source/style/start or another frame's property.
4. Join per-query contexts to the existing complete spacing values interface, then identify the remaining measurement request-trace/native object relation. No native heap, shaping or all-IEEE proof claim. No new finite matrices without a concrete risk.

Concrete gap witness will compare persistent versus reset/reseeded per-query states; it is a model-interface counterexample, not a Firefox bug. Actual cache refresh and lifetime remain explicit source obligations until connected.
