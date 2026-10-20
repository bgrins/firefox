window.runOverflowRelativeInitialDiagnostic = () => {
  const rows = [];
  for (const writingMode of ["horizontal-tb", "vertical-rl", "vertical-lr"]) {
  for (const layout of ["row", "column", "block"]) {
  for (const kind of ["overflow", "normal"]) {
  for (const [inlineOffset, blockOffset] of [[0, 0], [0, 17], [0, -17], [17, 0], [-17, 0]]) {
    const make = (initialInline, initialBlock) => {
      const columns = document.createElement("div");
      columns.className = "columns";
      columns.style.writingMode = writingMode;
      const parent = document.createElement("div");
      parent.className = `flow ${layout === "block" ? "block" : "flex"} ${layout} ${kind}`;
      const items = Array.from({length: 4}, () => {
        const item = document.createElement("div");
        item.className = "item";
        parent.append(item);
        return item;
      });
      const subject = items[0];
      subject.classList.add("subject");
      subject.style.insetInlineStart = `${initialInline}px`;
      subject.style.insetBlockStart = `${initialBlock}px`;
      const descendants = Array.from({length: 4}, () => {
        const child = document.createElement("div");
        child.className = "descendant";
        subject.append(child);
        return child;
      });
      columns.append(parent);
      document.body.append(columns);
      const capture = () => {
        const origin = columns.getBoundingClientRect();
        const rect = r => writingMode === "horizontal-tb" ?
          [r.left-origin.left, r.top-origin.top, r.width, r.height] :
          [r.top-origin.top, writingMode === "vertical-rl" ? origin.right-r.right : r.left-origin.left,
            r.height, r.width];
        const css = getComputedStyle(subject);
        return {columns: rect(origin).slice(2),
          descendants: descendants.map(child => rect(child.getBoundingClientRect())),
          descendantFragments: descendants.map(child => Array.from(child.getClientRects(), rect)),
          subjectFragments: Array.from(subject.getClientRects(), rect),
          parentFragments: Array.from(parent.getClientRects(), rect),
          otherItems: items.slice(1).map(child => rect(child.getBoundingClientRect())),
          computed: {writingMode: css.writingMode, position: css.position,
            inlineOffset: css.insetInlineStart, blockOffset: css.insetBlockStart}};
      };
      return {columns, subject, capture};
    };
    const freshFixture = make(inlineOffset, blockOffset);
    const fresh = freshFixture.capture();
    freshFixture.columns.remove();
    const dynamicFixture = make(0, 0);
    const zero = dynamicFixture.capture();
    dynamicFixture.subject.style.insetInlineStart = `${inlineOffset}px`;
    dynamicFixture.subject.style.insetBlockStart = `${blockOffset}px`;
    const dynamic = dynamicFixture.capture();
    dynamicFixture.subject.style.insetInlineStart = "0px";
    dynamicFixture.subject.style.insetBlockStart = "0px";
    const restored = dynamicFixture.capture();
    dynamicFixture.columns.remove();
    const differences = value => value.descendants.map((r, i) => r.map((v, a) => v-zero.descendants[i][a]));
    const freshDeltas = differences(fresh);
    const dynamicDeltas = differences(dynamic);
    const expected = [inlineOffset, blockOffset, 0, 0];
    rows.push({writingMode, layout, kind, inlineOffset, blockOffset,
      fresh, zero, dynamic, restored, freshDeltas, dynamicDeltas,
      calibrated: zero.columns.join() === "200,160" &&
        zero.descendants.every((r, i) => r.join() === [i*100,0,100,160].join()) &&
        zero.descendantFragments.every(r => r.length === 1),
      freshAndDynamicComputedEqual: JSON.stringify(fresh.computed) === JSON.stringify(dynamic.computed),
      freshAndDynamicGeometryEqual: JSON.stringify(fresh.descendantFragments) === JSON.stringify(dynamic.descendantFragments),
      freshTranslationMatches: freshDeltas.every(d => d.join() === expected.join()),
      dynamicTranslationMatches: dynamicDeltas.every(d => d.join() === expected.join()),
      allSizesPreserved: [...freshDeltas, ...dynamicDeltas].every(d => d[2] === 0 && d[3] === 0),
      otherItemsUnchanged: JSON.stringify(zero.otherItems) === JSON.stringify(fresh.otherItems) &&
        JSON.stringify(zero.otherItems) === JSON.stringify(dynamic.otherItems),
      restoredExactly: JSON.stringify(zero) === JSON.stringify(restored)});
  }
  }
  }
  }
  return rows;
};
