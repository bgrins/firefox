window.runOverflowSkipDiagnostic = () => {
  const columns = document.createElement("div");
  columns.className = "columns";
  columns.style.cssText = "writing-mode:vertical-rl;direction:ltr;--height:160px";
  const flex = document.createElement("div");
  flex.className = "flex row";
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
  document.body.append(columns);
  const rows = [];
  const record = stage => {
    const origin = columns.getBoundingClientRect();
    rows.push({stage, descendants: descendants.map(item => {
      const r = item.getBoundingClientRect();
      return [r.top - origin.top, origin.right - r.right, r.height, r.width];
    }), fragments: Array.from(flex.getClientRects(), r => [r.x, r.y, r.width, r.height])});
  };
  record("initial");
  items[3].style.blockSize = "81px";
  record("changed-item");
  items[3].style.blockSize = "80px";
  record("restored-item");
  items[3].style.minInlineSize = "99px";
  record("same-size");
  columns.remove();
  return rows;
};
