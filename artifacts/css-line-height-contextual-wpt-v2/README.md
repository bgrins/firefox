# Contextual line-height test split

The native one-file proposal is unchanged. This successor splits its 12 tests into ten unchanged random/special-value test bodies in css-values and two tree-counting tests in css-inline. Every old test name remains exactly once. The moved tree tests add independently positioned length controls and line-box geometry assertions, retaining all three insertion/removal snapshots before assertions.

The tree page contains no random() input and has no random-pref metadata dependency. The captured common WPT metadata enables tree counting and typed arithmetic; this is not a claim that the WPT harness is preference-free. The separate installed Firefox 158 release observation used unchanged random=false and supported all eight calibration inputs: both numeric tree expressions failed, their length equivalents and four ordinary controls passed. That saved observation was not execution of this revised WPT page.

The numeric and length targets are second children in separate holders. Prepending one element makes each third of three; removal restores second of two. Thus sibling-index and sibling-count each produce 2, 3, 2. At font-size 10px, both forms must produce 20px, 30px, 20px line-height and line-box height. No random sample inequality or parser-counter behavior is involved.

This remains one missing-context leaf-computation issue, with no new accepted fix or canonical Lean coverage. The sealed native patch and its spec/source limits remain authoritative. This package provides static validation only; root owns native builds and browser/WPT execution. Neither live source nor canonical WPT files were modified.
