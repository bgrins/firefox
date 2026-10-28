async function observeRoundNonfiniteClassification() {
  const context = "sign(1em - 16px)";
  const cases = [
    ["positive-infinities", "infinity", "infinity"],
    ["negative-infinities", "-infinity", "infinity"],
    ["contextual-infinities", `infinity * ${context}`, "infinity"],
    ["positive-finite-infinite-step", "1", "infinity"],
    ["negative-finite-infinite-step", "-1", "infinity"],
    ["zero-infinite-step", "0", "infinity"],
    ["nan-infinite-step", "NaN", "infinity"],
    ["contextual-finite-infinite-step", context, "infinity"],
    ["infinite-finite-step", "infinity", "1"],
    ["contextual-infinite-finite-step", `infinity * ${context}`, "1"],
    ["finite-zero-step", "1", "0"],
    ["finite-nan-step", "1", "NaN"],
    ["finite-contextual-step", "1", `infinity * ${context}`],
    ["infinite-contextual-step", "infinity", `infinity * ${context}`],
  ];
  const modes = ["nearest", "up", "down", "to-zero"];
  const numeric = (expression, font) => {
    if (expression === context) return Math.sign(font - 16);
    if (expression === `infinity * ${context}`) return Infinity * Math.sign(font - 16);
    return ({ infinity: Infinity, "-infinity": -Infinity, NaN: NaN })[expression] ?? Number(expression);
  };
  const token = value => Number.isNaN(value) ? "NaN" : value === Infinity ? "infinity" : value === -Infinity ? "-infinity" : String(value);
  const rounded = (mode, value, inputStep) => {
    const step = Math.abs(inputStep);
    if (Number.isNaN(value) || Number.isNaN(step) || step === 0) return NaN;
    if (!Number.isFinite(value)) return Number.isFinite(step) ? value : NaN;
    if (!Number.isFinite(step)) {
      if (value === 0 || mode === "nearest" || mode === "to-zero") return 0;
      return mode === "up" ? (value > 0 ? Infinity : 0) : (value < 0 ? -Infinity : 0);
    }
    const q = value / step;
    const k = mode === "up" ? Math.ceil(q) : mode === "down" ? Math.floor(q) : mode === "to-zero" ? Math.trunc(q) : Math.floor(q + 0.5);
    return k * step;
  };
  const encoded = value => Number.isNaN(value) ? 0 : 0.5 + 0.25 * Math.sign(value);
  const expression = (mode, value, step) => `calc(0.5 + 0.25 * sign(round(${mode}, ${value}, ${step})))`;
  const frame = document.createElement("iframe");
  frame.style.cssText = "width:320px;height:180px;border:0";
  frame.srcdoc = "<!doctype html><html><body style='margin:0'></body></html>";
  const loaded = new Promise(resolve => frame.addEventListener("load", resolve, { once: true }));
  document.documentElement.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const make = () => { const e = doc.createElement("div"); e.style.cssText = "position:absolute;width:1px;height:1px"; doc.body.append(e); return e; };
    const calibration = make();
    calibration.style.marginLeft = "calc(1em - 16px)";
    calibration.style.opacity = `calc(0.5 + 0.25 * ${context})`;
    const records = cases.flatMap(([id, value, step]) => modes.map(mode => {
      const target = make(), resolved = make(), literal = make();
      const authored = expression(mode, value, step);
      target.style.opacity = authored;
      return { id, value, step, mode, authored, target, resolved, literal };
    }));
    const snapshots = [];
    for (const [phase, font] of [8, 16, 32, 8].entries()) {
      doc.body.style.fontSize = `${font}px`;
      for (const r of records) {
        const value = numeric(r.value, font), step = numeric(r.step, font);
        r.resolvedExpression = expression(r.mode, token(value), token(step));
        r.expected = encoded(rounded(r.mode, value, step));
        r.resolved.style.opacity = r.resolvedExpression;
        r.literal.style.opacity = String(r.expected);
      }
      await new Promise(resolve => win.requestAnimationFrame(() => win.requestAnimationFrame(resolve)));
      const inputCalibration = { font: win.getComputedStyle(calibration).fontSize,
        difference: win.getComputedStyle(calibration).marginLeft,
        signEncoding: win.getComputedStyle(calibration).opacity,
        expectedDifference: `${font - 16}px`, expectedSignEncoding: encoded(Math.sign(font - 16)) };
      for (const r of records) {
        snapshots.push({ id: r.id, mode: r.mode, phase, font, authored: r.authored,
          resolvedExpression: r.resolvedExpression, expected: r.expected,
          supported: win.CSS.supports("opacity", r.authored), specified: r.target.style.opacity,
          actual: win.getComputedStyle(r.target).opacity, repeated: win.getComputedStyle(r.target).opacity,
          resolvedSupported: win.CSS.supports("opacity", r.resolvedExpression),
          resolvedSpecified: r.resolved.style.opacity, resolved: win.getComputedStyle(r.resolved).opacity,
          literal: win.getComputedStyle(r.literal).opacity, inputCalibration });
      }
    }
    return JSON.parse(JSON.stringify({ userAgent: navigator.userAgent, caseCount: records.length,
      snapshotCount: snapshots.length, unsupportedIsPass: false, nativeFixAccepted: false,
      encoding: "outer calc(0.5 + 0.25 * sign(round(...))); NaN censored to 0 at top level",
      snapshots }));
  } finally {
    frame.remove();
  }
}
