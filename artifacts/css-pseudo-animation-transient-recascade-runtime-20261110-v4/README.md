# Transient recascade runtime v4 preparation

Fresh inputs copied exclusively from frozen runtime v3. The sole fixture correction changes the query scroller from overflow:scroll to overflow-x:hidden; overflow-y:scroll. This removes the unnecessary horizontal scrollbar that caused five setup and four dependent result failures. All 14 native candidate files, all 208 query assertions, all 100 recascade assertions, all 130 ordinary WPT rows, runtime execution/restoration helpers and analyzers remain byte-identical.

GEOMETRY-AMENDMENT.json authenticates the frozen origin and exact replacement. GEOMETRY-AMENDMENT.patch replays after the existing source patches; check.py validates exact preservation and forward/reverse replay. CHECK-DELTA.patch is documentary and not applied to native sources. Execution HEAD and retained receipt remain unset for root's final freeze. No browser, native build or live mutation was performed in this preparation.

Preserve the v3 failed evidence and independent terminal review. No outcome waiver, assertion removal or native repair is included. Optimized build plus both complete direct fixtures and unchanged WPT remain required; public CSSOM and debug acceptance remain open.
