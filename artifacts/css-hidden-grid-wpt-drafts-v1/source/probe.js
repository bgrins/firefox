"use strict";

function measure(element, api) {
  if (api === "offset") {
    return [element.offsetWidth, element.offsetHeight];
  }
  const rect = element.getBoundingClientRect();
  return [rect.width, rect.height];
}

function same(actual, expected) {
  return actual.every((value, index) => value === expected[index]);
}

async function runGridDiagnostic() {
  const rows = [];
  for (const hidden of [false, true]) {
    for (const targetKind of ["item", "leaf"]) {
      for (const api of ["bounding", "offset"]) {
        const host = document.createElement("div");
        host.className = "host";
        const grid = document.createElement("div");
        grid.className = "grid";
        const item = document.createElement("div");
        item.className = "item";
        const leaf = document.createElement("div");
        leaf.className = "leaf";
        item.append(leaf);
        grid.append(item);
        host.append(grid);
        document.body.append(host);
        const target = targetKind === "leaf" ? leaf : item;
        const expected = width => targetKind === "leaf" ? [width / 2, 16] : [width, 32];
        const stages = [];
        function record(name, width) {
          const actual = measure(target, api);
          const wanted = expected(width);
          stages.push({ name, actual, expected: wanted, pass: same(actual, wanted) });
        }
        record("visible-calibration", 200);
        grid.style.contentVisibility = hidden ? "hidden" : "visible";
        record("initial-query", 200);
        host.style.width = "120px";
        const outerAfterMutation = host.getBoundingClientRect();
        const outer = [outerAfterMutation.width, outerAfterMutation.height];
        record("after-parent-width", 120);
        record("repeat-query", 120);
        grid.style.contentVisibility = "visible";
        record("shown-restoration", 120);
        rows.push({ hidden, targetKind, api, outer, outerExpected: [120, 32],
          outerPass: same(outer, [120, 32]), stages });
        host.remove();
      }
    }
  }
  const result = { rows, expectedRows: 8, expectedStages: 40,
    calibrationFailures: rows.filter(row => !row.outerPass || !row.stages[0].pass).length,
    targetMismatches: rows.reduce((sum, row) => sum + row.stages.slice(1).filter(stage => !stage.pass).length, 0) };
  window.gridDiagnosticResult = result;
  document.title = "Grid diagnostic complete";
  return result;
}

window.gridDiagnosticPromise = runGridDiagnostic();
