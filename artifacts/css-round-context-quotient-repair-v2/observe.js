async function observeRoundQuotientPrerequisite() {
  const frame = document.createElement("iframe");
  frame.srcdoc = "<!doctype html><body>";
  const loaded = new Promise(resolve => frame.onload = resolve);
  document.body.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const view = frame.contentWindow;
    const b = "0.3333333432674407958984375";
    const cases = [
      ["existing positive down", "down", 1, 0, b, 2 * Number(b)],
      ["existing positive to-zero", "to-zero", 1, 0, b, 2 * Number(b)],
      ["existing negative up", "up", -1, 1, b, 1 - 2 * Number(b)],
      ["existing negative to-zero", "to-zero", -1, 1, b, 1 - 2 * Number(b)],
      ["existing nearest control", "nearest", 1, 0, b, 1],
      ["existing exact-multiple control", "down", 1, 0, "0.25", 1],
    ].map(([name, mode, sign, offset, step, result]) => ({
      name, category: "existing-runtime-route", fonts: [16, 32, 16],
      expression: `calc(${offset} + round(${mode}, ${sign} * sign(1em - 16px), ${step}))`,
      resolved: font => `calc(${offset} + round(${mode}, ${sign * (font === 32 ? 1 : 0)}, ${step}))`,
      expected: font => font === 32 ? result : offset,
      input: "sign(1em - 16px)", inputExpected: font => font === 32 ? 1 : 0,
    }));
    for (const [mode, step, control] of [["down", b, false], ["to-zero", b, false], ["nearest", b, true], ["down", "0.25", true]]) {
      cases.push({
        name: `${control ? "exposure control" : "deferral exposure"} ${mode} ${step}`,
        category: control ? "deferral-control" : "predicted-deferral-exposure",
        fonts: [1, 0, 2, 1],
        expression: `sign(round(${mode}, 1em, ${step}em) - 0.8px)`,
        resolved: font => `sign(round(${mode}, ${font}px, ${Number(step) * font}px) - 0.8px)`,
        expected: font => font === 0 ? 0 : control ? 1 : font === 2 ? 1 : 0,
        input: "1", inputExpected: () => 1,
      });
    }
    const rows = [];
    for (const item of cases) {
      const target = doc.createElement("div");
      const resolved = doc.createElement("div");
      const literal = doc.createElement("div");
      const input = doc.createElement("div");
      doc.body.append(target, resolved, literal, input);
      target.style.opacity = item.expression;
      input.style.opacity = item.input;
      for (const font of item.fonts) {
        for (const node of [target, resolved, literal, input]) node.style.fontSize = `${font}px`;
        const resolvedExpression = item.resolved(font);
        resolved.style.opacity = "";
        resolved.style.opacity = resolvedExpression;
        literal.style.opacity = String(item.expected(font));
        rows.push({
          name: item.name, category: item.category, font, expression: item.expression,
          resolvedExpression, expected: item.expected(font), inputExpected: item.inputExpected(font),
          supports: view.CSS.supports("opacity", item.expression),
          resolvedSupports: view.CSS.supports("opacity", resolvedExpression),
          inputSupports: view.CSS.supports("opacity", item.input),
          specified: target.style.opacity, resolvedSpecified: resolved.style.opacity,
          inputSpecified: input.style.opacity, computedFont: view.getComputedStyle(target).fontSize,
          actual: Number(view.getComputedStyle(target).opacity),
          repeat: Number(view.getComputedStyle(target).opacity),
          resolved: Number(view.getComputedStyle(resolved).opacity),
          literal: Number(view.getComputedStyle(literal).opacity),
          input: Number(view.getComputedStyle(input).opacity),
        });
      }
      target.remove(); resolved.remove(); literal.remove(); input.remove();
    }
    return {cases: cases.length, snapshots: rows.length, rows};
  } finally {
    frame.remove();
  }
}
