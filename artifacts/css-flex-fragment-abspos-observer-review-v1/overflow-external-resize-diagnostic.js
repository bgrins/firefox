window.runOverflowExternalResizeDiagnostic = () => {
  const rows = [];
  for (const flexDirection of ["row", "column"]) {
    const outer = document.createElement("div");
    outer.className = "outer";
    const sibling = document.createElement("div");
    sibling.className = "sibling";
    sibling.style.width = "240px";
    const columns = document.createElement("div");
    columns.className = "columns";
    const flex = document.createElement("div");
    flex.className = `flex ${flexDirection}`;
    const items = Array.from({length: 4}, () => {
      const item = document.createElement("div");
      item.className = "item";
      flex.append(item);
      return item;
    });
    const descendants = Array.from({length: 4}, () => {
      const item = document.createElement("div");
      item.className = "descendant";
      items[0].append(item);
      return item;
    });
    columns.append(flex);
    outer.append(sibling, columns);
    document.body.append(outer);
    for (const [stage, width] of [["initial", 240], ["grow-column", 160],
                                  ["restore-column", 240], ["regrow-column", 160]]) {
      sibling.style.width = `${width}px`;
      const columnExtent = 400 - width;
      const origin = columns.getBoundingClientRect();
      const actual = descendants.map(item => {
        const r = item.getBoundingClientRect();
        return [r.top - origin.top, origin.right - r.right, r.height, r.width];
      });
      const reference = document.createElement("div");
      reference.className = "reference";
      reference.style.blockSize = `${columnExtent}px`;
      const references = descendants.map((_, i) => {
        const box = document.createElement("div");
        box.style.insetInlineStart = `${i * 100}px`;
        reference.append(box);
        return box;
      });
      document.body.append(reference);
      const refOrigin = reference.getBoundingClientRect();
      const expected = references.map(item => {
        const r = item.getBoundingClientRect();
        return [r.top - refOrigin.top, refOrigin.right - r.right, r.height, r.width];
      });
      reference.remove();
      rows.push({flexDirection, stage, columnExtent,
        columnSize: [origin.height, origin.width], actual, expected,
        calibrated: origin.height === 200 && origin.width === columnExtent &&
          expected.every((r, i) => r.join() === [i * 100, 0, 100, 160].join()),
        geometryOK: JSON.stringify(actual) === JSON.stringify(expected),
        fragments: Array.from(flex.getClientRects(), r => [r.x, r.y, r.width, r.height])});
    }
    outer.remove();
  }
  return rows;
};
