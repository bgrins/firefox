async function observeTreeCountingPartZero() {
  const frame = document.createElement("iframe");
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    doc.open();
    doc.write(`<!doctype html><style>
      #host::part(target) { width: calc(sibling-index() * 10px); height: calc(sibling-count() * 10px); border-left: 7px solid; }
    </style><div id="host"></div>`);
    doc.close();
    const win = frame.contentWindow;
    const root = doc.getElementById("host").attachShadow({mode: "open"});
    root.innerHTML = `<style>
      [part] { display: block; box-sizing: content-box; margin-left: calc(sibling-index() * 10px); padding-left: calc(sibling-count() * 10px); }
    </style><div id="holder"><i></i><div part="target"></div><i></i></div>`;
    const holder = root.getElementById("holder");
    const target = holder.children[1];
    const extra = doc.createElement("i");
    const snapshots = [];
    for (const phase of ["initial", "prepend", "restore"]) {
      if (phase === "prepend") holder.prepend(extra);
      if (phase === "restore") extra.remove();
      const read = () => {
        const s = win.getComputedStyle(target);
        return {width: s.width, height: s.height, marginLeft: s.marginLeft, paddingLeft: s.paddingLeft, borderLeftWidth: s.borderLeftWidth};
      };
      snapshots.push({phase, expectedIndex: phase === "prepend" ? 3 : 2,
        expectedCount: phase === "prepend" ? 4 : 3, first: read(), second: read()});
    }
    return JSON.parse(JSON.stringify({
      support: {index: win.CSS.supports("width", "calc(sibling-index() * 10px)"),
        count: win.CSS.supports("height", "calc(sibling-count() * 10px)")},
      authored: doc.styleSheets[0].cssRules[0].cssText,
      expectedOuterPixels: 0, snapshots
    }));
  } finally {
    frame.remove();
  }
}
