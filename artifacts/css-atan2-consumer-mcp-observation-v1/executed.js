async () => {
async function probeAtan2IntegerConsumers() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "position:fixed;left:0;top:0;width:320px;height:240px;border:0;visibility:hidden";
  const loaded = new Promise(resolve => frame.addEventListener("load", resolve, {once:true}));
  frame.srcdoc = "<!doctype html><style>html,body{margin:0;zoom:1}section{display:grid;grid-template-columns:repeat(8,20px)}div{height:1px;position:relative}</style>";
  document.documentElement.append(frame);
  try {
    await loaded;
    const win = frame.contentWindow;
    const doc = frame.contentDocument;
    const inputs = {em:"calc(1 + 2 * atan2(1em, 1em) / 45deg)",
      px:"calc(1 + 2 * atan2(1px, 1px) / 45deg)", literal:"3"};
    const rows = [];
    for (const consumer of ["steps", "subgrid", "z-index"]) {
      for (const [kind, count] of Object.entries(inputs)) {
        const host = doc.createElement("section");
        const target = doc.createElement("div");
        const reference = doc.createElement("div");
        host.append(target, reference);
        doc.body.append(host);
        const property = consumer === "steps" ? "animation-timing-function" :
          consumer === "subgrid" ? "grid-template-columns" : "z-index";
        const value = number => consumer === "steps" ? `steps(${number}, start)` :
          consumer === "subgrid" ? `subgrid repeat(${number}, [a])` : number;
        if (consumer === "subgrid") {
          for (const element of [target,reference]) {
            element.style.display = "grid";
            element.style.gridColumn = "1 / -1";
          }
        }
        target.style.setProperty(property,value(count));
        const snapshots = [];
        for (const font of [10,0,10]) {
          target.style.fontSize = `${font}px`;
          const expectedCount = kind === "em" && font === 0 ? 1 : 3;
          reference.style.setProperty(property,value(String(expectedCount)));
          const computed = win.getComputedStyle(target);
          snapshots.push({font, computedFont:computed.fontSize, expectedCount,
            actual:computed.getPropertyValue(property),
            reference:win.getComputedStyle(reference).getPropertyValue(property)});
        }
        rows.push({consumer,kind,property,value:value(count),
          supports:win.CSS.supports(property,value(count)),
          specified:target.style.getPropertyValue(property), snapshots});
      }
    }
    return {userAgent:navigator.userAgent, observationOnly:true, rows};
  } finally {
    frame.remove();
  }
}

return await probeAtan2IntegerConsumers();
}
