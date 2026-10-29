# Outer-tree counting observation

System Firefox 158.0, using the Firefox DevTools MCP default binary, returns 1 for both tree-counting functions in an outer ::part rule. Width and height therefore remain 10px in all three states: original tree, preceding sibling inserted, original tree restored. Repeated computed-style reads agree.

The same-tree margin and padding controls follow index 2/3/2 and count 3/4/3. A literal 7px border confirms the outer selector applies, and both functions pass CSS.supports. The current [CSS Values 5 tree-counting section](https://drafts.csswg.org/css-values-5/#tree-counting) specifies zero for a failed scoped reference. This is an observed current-spec discrepancy, not a candidate repair or a security-impact finding.

The probe ran in an owned about:blank tab, created and removed its own iframe, and the tab was closed afterward. The first attempted direct result-file save was rejected by the MCP path policy. A subsequent inline evaluation succeeded; its exact tool result is preserved here and the detached JSON was independently checked. No claim is made from the rejected save attempt.

This was not the local Firefox160 build and did not run WPT callbacks. The local original/candidate comparison, existing WPT update, and source acceptance remain pending. No native source, app, Git index or canonical control was changed by this observation.
