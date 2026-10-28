async function observeRemainingRandomBoundaries() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:400px;height:300px;border:0";
  frame.srcdoc = "<!doctype html><body></body>";
  const loaded = new Promise(resolve => frame.onload = resolve);
  document.body.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const cases = [
      ["radial-percentage-first", "background-image", key => `radial-gradient(random(${key}, 10%, 20%) 30%, red, blue)`, "indexed"],
      ["radial-explicit-ellipse", "background-image", key => `radial-gradient(ellipse random(${key}, 10%, 20%) 30%, red, blue)`, "indexed"],
      ["radial-length-first", "background-image", key => `radial-gradient(random(${key}, 10px, 20px) 30%, red, blue)`, "indexed"],
      ["radial-percentage-named", "background-image", key => `radial-gradient(random(${key}, 10%, 20%) 30%, red, blue)`, "named"],
      ["rotate-vector-first", "rotate", key => `random(${key}, 1, 2) 0 1 45deg`, "indexed"],
      ["rotate-angle-first", "rotate", key => `45deg random(${key}, 1, 2) 0 1`, "indexed"],
      ["rotate-angle-only", "rotate", key => `random(${key}, 10deg, 90deg)`, "indexed"],
      ["rotate-vector-named", "rotate", key => `random(${key}, 1, 2) 0 1 45deg`, "named"],
    ];
    const rows = [];
    for (const [id, property, expression, kind] of cases) {
      const key = kind === "named" ? `--boundary-${id}` : "property-index-scoped";
      const keys = [key, kind === "named" ? key : `ua-${property}-1`, `ua-${property}-2`, `ua-${property}-3`];
      const values = keys.map(expression);
      const elements = values.map(value => {
        const element = doc.createElement("div");
        element.style.cssText = "width:200px;height:100px;font-size:10px";
        element.style.setProperty(property, value);
        doc.body.append(element);
        return element;
      });
      const specified = elements.map(e => e.style.getPropertyValue(property));
      const computed = elements.map(e => win.getComputedStyle(e).getPropertyValue(property));
      rows.push({id, property, kind, authored: values,
        supported: values.map(value => win.CSS.supports(property, value)),
        specified, computed, specifiedMatchesExpected: specified[0] === specified[1],
        computedMatchesExpected: computed[0] === computed[1],
        matchingExplicitIndexes: [1, 2, 3].filter(i => specified[0] === specified[i]),
        computedMatchingExplicitIndexes: [1, 2, 3].filter(i => computed[0] === computed[i])});
      elements.forEach(e => e.remove());
    }
    return {schema: 1, userAgent: win.navigator.userAgent, rows,
      limitations: "Observation only; same-key comparisons. Distinct random samples may coincide. The named rows use an identical named reference, not a numbered key. No native candidate was installed by this function."};
  } finally {
    frame.remove();
  }
}
