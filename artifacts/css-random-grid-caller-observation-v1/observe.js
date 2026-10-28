async function observeRandomGridCallerRollback() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:500px;height:400px;border:0";
  frame.srcdoc = "<!doctype html><body></body>";
  const loaded = new Promise(resolve => frame.onload = resolve);
  document.body.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const cases = [
      ["rows-before-auto-flow", k => `random(${k(1)}, 10px, 20px) / auto-flow 100px`, "indexed"],
      ["two-rows-before-auto-flow", k => `random(${k(1)}, 10px, 20px) random(${k(2)}, 30px, 40px) / auto-flow 100px`, "indexed"],
      ["both-axes-auto-flow", k => `random(${k(1)}, 10px, 20px) / auto-flow random(${k(2)}, 30px, 40px)`, "indexed"],
      ["explicit-template-control", k => `random(${k(1)}, 10px, 20px) / 100px`, "indexed"],
      ["auto-flow-first-control", k => `auto-flow random(${k(1)}, 10px, 20px) / 100px`, "indexed"],
      ["named-control", k => `random(${k(1)}, 10px, 20px) / auto-flow 100px`, "named"],
      ["fixed-control", k => `random(${k(1)}, 10px, 20px) / auto-flow 100px`, "fixed"],
    ];
    const properties = ["grid-template-rows", "grid-template-columns", "grid-auto-rows", "grid-auto-columns", "grid-auto-flow"];
    const rows = [];
    for (const [id, expression, kind] of cases) {
      const actualKey = kind === "named" ? "--grid-caller" : kind === "fixed" ? "fixed 0.25" : "property-index-scoped";
      const authored = [expression(() => actualKey), ...[0, 1, 2].map(shift => expression(index => kind === "indexed" ? `ua-grid-${index + shift}` : actualKey))];
      const elements = authored.map(value => {
        const element = doc.createElement("div");
        element.style.cssText = "display:grid;width:200px;justify-content:start;align-content:start;font-size:10px";
        element.style.setProperty("grid", value);
        element.append(doc.createElement("div"));
        doc.body.append(element);
        return element;
      });
      const specified = elements.map(element => Object.fromEntries(properties.map(property => [property, element.style.getPropertyValue(property)])));
      const computed = elements.map(element => {
        const style = win.getComputedStyle(element);
        return Object.fromEntries(properties.map(property => [property, style.getPropertyValue(property)]));
      });
      const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
      rows.push({id, kind, authored, supported: authored.map(value => win.CSS.supports("grid", value)), specified, computed,
        specifiedMatchesExpected: equal(specified[0], specified[1]), computedMatchesExpected: equal(computed[0], computed[1]),
        matchingReferenceShifts: [0, 1, 2].filter(shift => equal(specified[0], specified[shift + 1])),
        computedMatchingReferenceShifts: [0, 1, 2].filter(shift => equal(computed[0], computed[shift + 1]))});
      elements.forEach(element => element.remove());
    }
    return {schema: 1, userAgent: win.navigator.userAgent, rows,
      limitations: "Same-key comparison only. Different keys may coincidentally produce equal values. Named/fixed reference shifts repeat the same control. No candidate source is installed by this function."};
  } finally {
    frame.remove();
  }
}
