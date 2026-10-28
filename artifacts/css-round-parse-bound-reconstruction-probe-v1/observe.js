async function observeRoundParseBounds() {
  const cases = [
    ["positive-up", "round(up, .65, .1)", ".7", 1],
    ["positive-nearest", "round(nearest, .66, .1)", ".7", 1],
    ["negative-down", "round(down, -.65, .1)", "-.7", -1],
    ["negative-nearest", "round(nearest, -.66, .1)", "-.7", -1],
    ["positive-down-control", "round(down, .65, .1)", ".6", 1],
    ["positive-to-zero-control", "round(to-zero, .65, .1)", ".6", 1],
    ["exact-step-control", "round(up, .65, .125)", ".75", 1],
    ["explicit-dyadic-up", "round(up, 0.64999997615814208984375, 0.100000001490116119384765625)", "calc(7 * 0.100000001490116119384765625)", 1],
  ];
  const frame = document.createElement("iframe");
  frame.setAttribute("aria-hidden", "true");
  frame.srcdoc = "<!doctype html><html><body></body></html>";
  const loaded = new Promise(resolve => frame.addEventListener("load", resolve, { once: true }));
  document.documentElement.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const records = cases.map(([id, expression, reference, direction]) => {
      const difference = direction > 0 ? `${expression} - ${reference}` : `${reference} - ${expression}`;
      const inputs = {
        target: `sign(${difference})`,
        reference: `sign(${reference} - ${reference})`,
        literalZero: "0",
        literalOne: "1",
        nonzeroAmplifier: "sign(0.7000000476837158203125 - 0.699999988079071044921875)",
      };
      const elements = Object.fromEntries(Object.entries(inputs).map(([name, value]) => {
        const element = doc.createElement("div");
        element.style.opacity = value;
        doc.body.append(element);
        return [name, element];
      }));
      const direct = doc.createElement("div");
      direct.style.zIndex = `calc(${expression} * 10000000)`;
      doc.body.append(direct);
      return { id, expression, reference, direction, inputs, elements, direct };
    });
    const rows = records.map(record => {
      const support = Object.fromEntries(Object.entries(record.inputs).map(([name, value]) => [name, win.CSS.supports("opacity", value)]));
      const specified = Object.fromEntries(Object.entries(record.elements).map(([name, element]) => [name, element.style.opacity]));
      const first = Object.fromEntries(Object.entries(record.elements).map(([name, element]) => [name, win.getComputedStyle(element).opacity]));
      const repeat = Object.fromEntries(Object.entries(record.elements).map(([name, element]) => [name, win.getComputedStyle(element).opacity]));
      return { id: record.id, expression: record.expression, referenceExpression: record.reference,
        inputs: record.inputs, support, specified, first, repeat,
        directScaledInteger: { supported: win.CSS.supports("z-index", `calc(${record.expression} * 10000000)`),
          specified: record.direct.style.zIndex, computed: win.getComputedStyle(record.direct).zIndex },
        calibrated: Object.values(support).every(Boolean) && Object.values(specified).every(Boolean) &&
          first.reference === "0" && first.literalZero === "0" && first.literalOne === "1" && first.nonzeroAmplifier === "1" &&
          JSON.stringify(first) === JSON.stringify(repeat),
        expectedTarget: "0", matchesExpected: first.target === "0" };
    });
    return { purpose: "Constant finite Round parse-bound reconstruction; exact represented-dyadic oracle", rows };
  } finally {
    frame.remove();
  }
}
