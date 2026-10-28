async function observeRoundInfiniteValueKnowledge() {
  const frame = document.createElement("iframe");
  frame.srcdoc = "<!doctype html><html><body style='margin:0'></body></html>";
  const loaded = new Promise(resolve => frame.addEventListener("load", resolve, { once: true }));
  document.documentElement.append(frame);
  try {
    await loaded;
    const doc = frame.contentDocument;
    const win = frame.contentWindow;
    const make = () => {
      const element = doc.createElement("div");
      doc.body.append(element);
      return element;
    };
    const encode = value => `calc(0.5 + 0.25 * sign(${value}))`;
    const calibration = make();
    calibration.style.width = "1em";
    calibration.style.opacity = encode("NaN");
    const rows = [];
    for (const mode of ["nearest", "up", "down", "to-zero"]) {
      for (const sign of [1, -1]) {
        const infinity = sign === 1 ? "infinity" : "-infinity";
        for (const kind of ["nan-step", "relative-leaf-step", "fixed-finite-step"]) {
          const value = kind === "nan-step" ? infinity : `${infinity} * 1px`;
          const step = kind === "nan-step" ? "NaN" : kind === "relative-leaf-step" ? "1em" : "8px";
          const authored = encode(`round(${mode}, ${value}, ${step})`);
          const target = make(), resolved = make(), literal = make();
          target.style.opacity = authored;
          rows.push({ mode, sign, kind, value, authored, target, resolved, literal });
        }
      }
    }
    const snapshots = [];
    for (const [phase, font] of [8, 0, 8].entries()) {
      doc.body.style.fontSize = `${font}px`;
      for (const row of rows) {
        const step = row.kind === "nan-step" ? "NaN" : row.kind === "relative-leaf-step" ? `${font}px` : "8px";
        row.resolvedExpression = encode(`round(${row.mode}, ${row.value}, ${step})`);
        row.expected = row.kind === "nan-step" || (row.kind === "relative-leaf-step" && font === 0)
          ? 0 : 0.5 + 0.25 * row.sign;
        row.resolved.style.opacity = row.resolvedExpression;
        row.literal.style.opacity = String(row.expected);
      }
      const inputCalibration = {
        font: win.getComputedStyle(calibration).fontSize,
        width: win.getComputedStyle(calibration).width,
        nanEncoding: win.getComputedStyle(calibration).opacity,
        nanSupported: win.CSS.supports("opacity", encode("NaN")),
        nanSpecified: calibration.style.opacity,
      };
      for (const row of rows) {
        snapshots.push({
          kind: row.kind, mode: row.mode, sign: row.sign, phase, font,
          authored: row.authored, supported: win.CSS.supports("opacity", row.authored),
          specified: row.target.style.opacity, actual: win.getComputedStyle(row.target).opacity,
          repeated: win.getComputedStyle(row.target).opacity,
          resolvedExpression: row.resolvedExpression,
          resolvedSupported: win.CSS.supports("opacity", row.resolvedExpression),
          resolvedSpecified: row.resolved.style.opacity,
          resolved: win.getComputedStyle(row.resolved).opacity,
          expected: row.expected, literal: win.getComputedStyle(row.literal).opacity,
          inputCalibration,
        });
      }
    }
    return JSON.parse(JSON.stringify({ userAgent: navigator.userAgent, caseCount: rows.length,
      snapshotCount: snapshots.length, unsupportedIsPass: false,
      note: "Resolved NaN-step Round is diagnostic too; only direct NaN encoding, literal, font and width are calibration.",
      snapshots }));
  } finally {
    frame.remove();
  }
}
