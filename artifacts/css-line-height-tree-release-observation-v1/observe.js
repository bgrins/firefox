async () => {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:400px;height:300px;border:0";
  frame.srcdoc = "<!doctype html><body></body>";
  const loaded = new Promise(resolve => frame.onload = resolve);
  document.body.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument, win = frame.contentWindow;
    const cases = [
      ["literal", "2", [20, 20, 20]],
      ["calc literal", "calc(2)", [20, 20, 20]],
      ["percentage ratio", "calc(100% / 1em)", [10, 10, 10]],
      ["inherited lh ratio", "calc(1lh / 1em)", [40, 40, 40]],
      ["sibling index number", "sibling-index()", [20, 30, 20]],
      ["sibling count number", "sibling-count()", [20, 30, 20]],
      ["sibling index length", "calc(sibling-index() * 1em)", [20, 30, 20]],
      ["sibling count length", "calc(sibling-count() * 1em)", [20, 30, 20]],
    ];
    const rows = [];
    for (const [id, value, expected] of cases) {
      const holder = doc.createElement("div");
      holder.style.cssText = "font:10px monospace;line-height:40px";
      holder.append(doc.createElement("div"));
      const target = doc.createElement("div");
      target.style.lineHeight = value;
      target.textContent = "x";
      holder.append(target); doc.body.append(holder);
      const measure = () => ({lineHeight: win.getComputedStyle(target).lineHeight,
        fontSize: win.getComputedStyle(target).fontSize, height: target.getBoundingClientRect().height});
      const snapshots = [measure()];
      const added = doc.createElement("div"); holder.prepend(added);
      snapshots.push(measure()); added.remove(); snapshots.push(measure());
      rows.push({id, value, supported:win.CSS.supports("line-height", value), specified:target.style.lineHeight, expected, snapshots});
      holder.remove();
    }
    return JSON.parse(JSON.stringify({userAgent:win.navigator.userAgent,
      randomSupported:win.CSS.supports("line-height", "random(--release-probe, 1, 3)"), rows}));
  } finally { frame.remove(); }
}