async function probeAttributeFallbackTaint() {
  const url = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
  const literal = JSON.stringify(url);
  const cases = [
    { name: "literal", expression: literal, tainted: false },
    { name: "raw-primary", expression: `attr(data-value raw-string, ${literal})`, value: url, tainted: true },
    { name: "missing-raw-fallback", expression: `attr(data-absent raw-string, ${literal})`, tainted: true },
    { name: "invalid-typed-fallback", expression: `attr(data-value type(<length>), ${literal})`, value: url, tainted: true },
    { name: "missing-typed-fallback", expression: `attr(data-absent type(<string>), ${literal})`, tainted: true },
    { name: "typed-primary", expression: `attr(data-value type(<string>), ${literal})`, value: literal, tainted: true },
    { name: "var-literal-fallback", expression: `var(--missing, ${literal})`, tainted: false },
    { name: "nested-attr-fallback", expression: "attr(data-absent raw-string, attr(data-value raw-string))", value: url, tainted: true },
  ];
  const rows = [];
  for (const mode of ["direct", "unregistered", "registered"]) {
    for (const scenario of cases) {
      const iframe = document.createElement("iframe");
      document.body.append(iframe);
      try {
        const doc = iframe.contentDocument;
        doc.open();
        doc.write("<!doctype html><meta charset=utf-8><title>Fallback taint</title><body>");
        doc.close();
        if (mode === "registered") {
          const style = doc.createElement("style");
          style.textContent = '@property --source { syntax: "<string>"; inherits: false; initial-value: "clean"; }';
          doc.head.append(style);
        }
        const target = doc.createElement("div");
        if (scenario.value !== undefined) {
          target.setAttribute("data-value", scenario.value);
        }
        if (mode !== "direct") {
          target.style.setProperty("--source", scenario.expression);
        }
        target.style.backgroundImage = `image-set(${mode === "direct" ? scenario.expression : "var(--source)"})`;
        const control = doc.createElement("div");
        control.style.backgroundImage = `image-set(${literal})`;
        doc.body.append(target, control);
        const computed = iframe.contentWindow.getComputedStyle(target);
        const actual = computed.backgroundImage;
        const controlValue = iframe.contentWindow.getComputedStyle(control).backgroundImage;
        const expected = scenario.tainted ? "none" : controlValue;
        rows.push({
          mode, name: scenario.name, expression: scenario.expression,
          specified: target.style.backgroundImage,
          source: computed.getPropertyValue("--source"),
          actual, expected, controlValue,
          controlValid: controlValue !== "none" && control.style.backgroundImage !== "",
          matchesExpected: actual === expected,
        });
      } finally {
        iframe.remove();
      }
    }
  }
  return {
    userAgent: navigator.userAgent,
    support: {
      imageSet: CSS.supports("background-image", `image-set(${literal})`),
      rawAttr: CSS.supports("content", 'attr(data-value raw-string, "fallback")'),
      typedAttr: CSS.supports("width", "attr(data-value type(<length>), 1px)"),
      propertyRule: "CSSPropertyRule" in window,
    },
    rows,
  };
}
