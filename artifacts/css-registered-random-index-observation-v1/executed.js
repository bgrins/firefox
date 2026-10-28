async function observeRegisteredRandomKeys() {
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:320px;height:180px;border:0";
  document.body.append(frame);
  try {
    const doc = frame.contentDocument;
    doc.open();
    doc.write("<!doctype html><body>");
    doc.close();
    const win = frame.contentWindow;
    const support = {
      random: win.CSS.supports("opacity", "random(fixed .25, 0, 1)"),
      indexed: win.CSS.supports("opacity", "random(property-index-scoped, 0, 1)"),
      explicit: win.CSS.supports("opacity", "random(ua-probe-1, 0, 1)"),
      registerProperty: typeof win.CSS.registerProperty === "function",
    };
    if (Object.values(support).some(value => !value)) return {support, rows: [], unavailable: true};
    const random = "random(property-index-scoped, 0, 1)";
    const cases = [
      ["single", "<number>", random, "indexed"],
      ["number-first", "<number> | <length>", random, "indexed"],
      ["length-first", "<length> | <number>", random, "indexed"],
      ["two-failed", "<length> | <angle> | <number>", random, "indexed"],
      ["list", "<number>+", `${random} ${random}`, "list"],
      ["failed-list", "<length>+ | <number>+", `${random} ${random}`, "list"],
      ["named", "<length> | <number>", "random(--shared-probe, 0, 1)", "named"],
      ["fixed", "<length> | <number>", "random(fixed .25, 0, 1)", "fixed"],
      ["property", "<length> | <number>", "random(property-scoped, 0, 1)", "property"],
      ["auto", "<number>", "random(0, 1)", "admission"],
      ["element", "<number>", "random(element-scoped, 0, 1)", "admission"],
      ["decl-single", "<number>", "0.25", "indexed", random],
      ["decl-length-first", "<length> | <number>", "0.25", "indexed", random],
      ["decl-two-failed", "<length> | <angle> | <number>", "0.25", "indexed", random],
      ["decl-failed-list", "<length>+ | <number>+", "0.25 0.75", "list", `${random} ${random}`],
    ];
    const active = [];
    const rows = [];
    for (const [id, syntax, initialValue, kind, declaration = initialValue] of cases) {
      const name = `--random-key-probe-${id}`;
      let registrationError = null;
      try { win.CSS.registerProperty({name, syntax, inherits: false, initialValue}); }
      catch (error) { registrationError = {name: error.name, message: error.message}; }
      const initial = doc.createElement("div");
      const declared = doc.createElement("div");
      declared.style.setProperty(name, declaration);
      doc.body.append(initial, declared);
      const reference = key => {
        const element = doc.createElement("div");
        element.style.opacity = `random(${key}, 0, 1)`;
        doc.body.append(element);
        return element;
      };
      const indexed = [1, 2, 3, 4].map(index => reference(`ua-${name}-${index}`));
      const property = reference(`ua-${name}`);
      const named = reference("--shared-probe");
      active.push({id, name, syntax, initialValue, declaration, kind, registrationError, initial, declared, indexed, property, named});
    }
    const capture = async phase => {
      await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
      for (const item of active) {
        const opacity = element => ({specified: element.style.opacity, computed: win.getComputedStyle(element).opacity});
        const keys = item.indexed.map(opacity);
        const property = opacity(item.property);
        const named = opacity(item.named);
        const expected = item.kind === "indexed" ? [keys[0].computed]
          : item.kind === "list" ? keys.slice(0, 2).map(value => value.computed)
          : item.kind === "property" ? [property.computed]
          : item.kind === "named" ? [named.computed]
          : item.kind === "fixed" ? ["0.25"] : null;
        rows.push({phase, id: item.id, name: item.name, syntax: item.syntax,
          initialValue: item.initialValue, declaration: item.declaration, registrationError: item.registrationError,
          initial: win.getComputedStyle(item.initial).getPropertyValue(item.name).trim(),
          declared: win.getComputedStyle(item.declared).getPropertyValue(item.name).trim(),
          declaredSpecified: item.declared.style.getPropertyValue(item.name),
          explicitKeys: keys, property, named, expected,
          expectedInitial: item.id.startsWith("decl-") ? item.initialValue.split(/\s+/) : expected,
          expectedDeclared: expected});
      }
    };
    await capture("registered");
    win.CSS.registerProperty({name: "--random-key-rebuild-control", syntax: "<number>", inherits: false, initialValue: "17"});
    await capture("after-unrelated-registration");
    const style = doc.createElement("style");
    style.textContent = "body { color: rgb(1, 2, 3); }";
    doc.head.append(style);
    await capture("after-stylesheet-change");
    return {support, unavailable: false, cases: cases.length, rows};
  } finally {
    frame.remove();
  }
}
