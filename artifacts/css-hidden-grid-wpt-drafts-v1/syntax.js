
"use strict";
window.gridQueryResults = [];
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

const cases = [
  {"hidden": false, "targetKind": "item", "api": "bounding", "name": "Grid own-content query: visible, direct item, bounding"},
  {"hidden": false, "targetKind": "item", "api": "offset", "name": "Grid own-content query: visible, direct item, offset"},
  {"hidden": false, "targetKind": "leaf", "api": "bounding", "name": "Grid own-content query: visible, leaf-first, bounding"},
  {"hidden": false, "targetKind": "leaf", "api": "offset", "name": "Grid own-content query: visible, leaf-first, offset"},
  {"hidden": true, "targetKind": "item", "api": "bounding", "name": "Grid own-content query: hidden, direct item, bounding"},
  {"hidden": true, "targetKind": "item", "api": "offset", "name": "Grid own-content query: hidden, direct item, offset"},
  {"hidden": true, "targetKind": "leaf", "api": "bounding", "name": "Grid own-content query: hidden, leaf-first, bounding"},
  {"hidden": true, "targetKind": "leaf", "api": "offset", "name": "Grid own-content query: hidden, leaf-first, offset"}
];
for (const c of cases) {
  test(t => {
    assert_true(CSS.supports("display", "grid"), "calibration: grid support");
    assert_true(CSS.supports("content-visibility", "hidden"), "calibration: hidden support");
    const {hidden, targetKind, api} = c;
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
    t.add_cleanup(() => host.remove());
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
    window.gridQueryResults.push({name: c.name, hidden, targetKind, api, outer,
                                  outerExpected: [120, 32], stages});
    assert_array_equals(stages[0].actual, stages[0].expected, "calibration: initial visible target");
    assert_array_equals(outer, [120, 32], "calibration: visible parent after width mutation");
    assert_array_equals(stages[4].actual, stages[4].expected, "calibration: shown target restoration");
    for (const stage of stages.slice(1, 4)) {
      assert_array_equals(stage.actual, stage.expected,
                          `${hidden ? "selected query" : "calibration: visible control"}: ${stage.name}`);
    }
  }, c.name);
}
