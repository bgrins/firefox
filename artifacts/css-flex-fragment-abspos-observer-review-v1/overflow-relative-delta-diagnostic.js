window.runOverflowRelativeDeltaDiagnostic = () => {
  const rows = [];
  const expectedZero = Array.from({length: 4}, (_, i) => [i * 100, 0, 100, 160]);
  for (const layout of ["row", "column", "block"]) {
    for (const kind of ["overflow", "normal"]) {
      const columns = document.createElement("div");
      columns.className = "columns";
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
        const rect = r => [r.left - origin.left, r.top - origin.top, r.width, r.height];
        return {
          columns: [origin.width, origin.height],
          descendants: descendants.map(child => rect(child.getBoundingClientRect())),
          descendantFragments: descendants.map(child => Array.from(child.getClientRects(), rect)),
          subjectFragments: Array.from(subject.getClientRects(), rect),
          parentFragments: Array.from(parent.getClientRects(), rect),
          otherItems: items.slice(1).map(child => rect(child.getBoundingClientRect())),
          computed: {position: getComputedStyle(subject).position,
            inlineOffset: getComputedStyle(subject).insetInlineStart,
            blockOffset: getComputedStyle(subject).insetBlockStart}
        };
      };
      subject.style.insetInlineStart = "0px";
      subject.style.insetBlockStart = "0px";
      const zero = capture();
      for (const [inlineOffset, blockOffset] of [[0, 0], [0, 17], [0, -17], [17, 0], [-17, 0]]) {
        subject.style.insetInlineStart = `${inlineOffset}px`;
        subject.style.insetBlockStart = `${blockOffset}px`;
        const shifted = capture();
        subject.style.insetInlineStart = "0px";
        subject.style.insetBlockStart = "0px";
        const restored = capture();
        const deltas = shifted.descendants.map((r, i) => r.map((v, axis) => v - zero.descendants[i][axis]));
        rows.push({layout, kind, inlineOffset, blockOffset, zero, shifted, restored, deltas,
          calibrated: JSON.stringify(zero.descendants) === JSON.stringify(expectedZero) &&
            zero.columns.join() === "200,160" &&
            zero.descendantFragments.every(fragments => fragments.length === 1),
          sizesPreserved: deltas.every(d => d[2] === 0 && d[3] === 0),
          expectedTranslation: [inlineOffset, blockOffset, 0, 0],
          translationMatches: deltas.every(d => d.join() === [inlineOffset, blockOffset, 0, 0].join()),
          otherItemsUnchanged: JSON.stringify(zero.otherItems) === JSON.stringify(shifted.otherItems),
          restoredExactly: JSON.stringify(zero) === JSON.stringify(restored)});
      }
      columns.remove();
    }
  }
  return rows;
};
