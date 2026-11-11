# Root review of scroll-geometry amendment

PASS for execution preparation. Root authenticated all 73 preparation files and checked every native source/candidate role, runner, restoration helper, analyzer, expected WPT record and assertion inventory against frozen v3. The only fixture change replaces overflow:scroll with overflow-x:hidden and overflow-y:scroll. All 208 query, 100 recascade and 130 WPT expectations remain intact.

The failed v3 trace reported a 215-pixel scroll range where the fixture expected 200. A horizontal classic scrollbar reduces the 100-pixel scrollport height to 85, yielding the recorded 100/215 and 200/215 scroll-timeline fractions. ViewTimeline's corresponding 185-pixel cover range explains the named-range setup failures. The revised geometry retains block scrolling and removes the unrelated horizontal gutter, rather than accepting the failed samples.

Root inspected CHECK-DELTA.patch and independently reran the source/patch/76-parser-control preparation. Freeze then verified clean execution HEAD and the restored retained browser receipt. The resulting 70-input runtime manifest is 2fa2939357b708381b7ad1b2f2fa8e816ef5faa5d9d2ee7e4568e001bf3370ff. Native/runtime acceptance requires the separate execution and restoration records; no success is inferred here.
