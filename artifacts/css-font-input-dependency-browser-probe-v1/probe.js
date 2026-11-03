async () => {
  const frame = document.createElement("iframe");
  frame.srcdoc = '<!doctype html><meta charset="utf-8"><style></style><div id="parent"><div id="target" data-value="var(--unit)"></div><div id="reference"></div></div>';
  const loaded = new Promise(resolve => frame.onload = resolve);
  document.body.append(frame);
  await loaded;
  try {
    const win = frame.contentWindow;
    const doc = frame.contentDocument;
    win.CSS.registerProperty({name: "--unit", syntax: "<length>", inherits: false, initialValue: "0px"});
    const target = doc.getElementById("target");
    const reference = doc.getElementById("reference");
    const rows = [];
    for (const [property, fallback] of [["appearance", "none"], ["direction", "ltr"],
      ["text-orientation", "mixed"], ["writing-mode", "horizontal-tb"],
      ["font-family", "serif"], ["font-weight", "normal"]]) {
      for (const form of ["absolute", "variable", "percentage", "inherited"]) {
        for (const size of [20, 30]) {
          const fontSize = form === "absolute" ? `${size}px` :
            form === "variable" ? "var(--size)" : form === "percentage" ? "100%" : "inherit";
          doc.querySelector("style").textContent = `
            #parent { font-size: ${size}px; font-family: serif; }
            #target, #reference { --unit: 1em; --size: ${size}px; font-size: ${fontSize}; }
            #target { ${property}: attr(data-value type(<length>), ${fallback}); }
            #reference { ${property}: ${fallback}; }`;
          const first = win.getComputedStyle(target).getPropertyValue("--unit");
          rows.push({property, form, size, first,
            targetFontSize: win.getComputedStyle(target).fontSize,
            reference: win.getComputedStyle(reference).getPropertyValue("--unit"),
            actualProperty: win.getComputedStyle(target).getPropertyValue(property),
            syntaxSupported: win.CSS.supports(property, `attr(data-value type(<length>), ${fallback})`)});
        }
      }
    }
    return {userAgent: navigator.userAgent, compatMode: doc.compatMode, rows};
  } finally {
    frame.remove();
  }
}
