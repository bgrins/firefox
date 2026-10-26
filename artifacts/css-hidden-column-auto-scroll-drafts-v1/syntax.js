
"use strict";
window.columnAutoScrollResults = [];
const cases = [
  {"name": "Auto-skipped table scroll provider: col, no-change", "kind": "col", "change": false},
  {"name": "Auto-skipped table scroll provider: col, width-change", "kind": "col", "change": true},
  {"name": "Auto-skipped table scroll provider: colgroup, no-change", "kind": "colgroup", "change": false},
  {"name": "Auto-skipped table scroll provider: colgroup, width-change", "kind": "colgroup", "change": true}
];
function fixture(c, changed = false) {
  const scroller = document.createElement("div");
  scroller.className = "scroller";
  const columns = c.kind === "col" ?
    '<colgroup><col><col class="selected"><col></colgroup>' :
    '<colgroup span="1"></colgroup><colgroup class="selected" span="1"></colgroup><colgroup span="1"></colgroup>';
  scroller.innerHTML = `<div class="leading"></div><div class="subject"><table${changed ? ' class="narrow"' : ""}>${columns}<tbody><tr><td></td><td></td><td></td></tr></tbody></table></div><div class="trailing"></div>`;
  document.body.append(scroller);
  return {scroller, subject: scroller.querySelector(".subject"),
          table: scroller.querySelector("table"), target: scroller.querySelector(".selected"),
          cells: [...scroller.querySelectorAll("td")]};
}
function rect(element) {
  const r = element.getBoundingClientRect();
  return [r.x, r.y, r.width, r.height];
}
function offset(f) {
  return [f.scroller.scrollLeft, f.scroller.scrollTop];
}
function waitSkipped(t, f, events) {
  return new Promise((resolve, reject) => {
    const timer = t.step_timeout(() => reject(new Error("calibration: no skipped=true event within 3000ms")), 3000);
    const listener = event => {
      events.push({skipped: event.skipped, trusted: event.isTrusted});
      if (event.skipped) {
        clearTimeout(timer);
        resolve();
      }
    };
    f.subject.addEventListener("contentvisibilityautostatechange", listener);
    t.add_cleanup(() => {
      clearTimeout(timer);
      f.subject.removeEventListener("contentvisibilityautostatechange", listener);
    });
  });
}
const scrollOptions = {block: "start", inline: "start", behavior: "instant"};
for (const c of cases) {
  promise_test(async t => {
    assert_true(CSS.supports("content-visibility", "auto"), "calibration: auto support");
    assert_true(CSS.supports("scrollbar-width", "none"), "calibration: scrollbar geometry support");
    const f = fixture(c);
    t.add_cleanup(() => f.scroller.remove());
    const result = {name: c.name, events: []};
    window.columnAutoScrollResults.push(result);
    result.warm = {outer: rect(f.scroller), subject: rect(f.subject),
                   target: rect(f.target), cells: f.cells.map(rect), offset: offset(f)};
    assert_array_equals(result.warm.outer, [0, 0, 100, 100], "calibration: warm scroller");
    assert_array_equals(result.warm.subject, [0, 8000, 600, 80], "calibration: explicit subject size");
    assert_array_equals(result.warm.target, [160, 8000, 160, 40], "calibration: warm column/group");
    for (let i = 0; i < 3; ++i) {
      assert_array_equals(result.warm.cells[i], [160 * i, 8000, 160, 40], `calibration: warm cell ${i}`);
    }
    assert_array_equals(result.warm.offset, [0, 0], "calibration: initial scroll position");
    assert_equals(f.scroller.clientWidth, 100, "calibration: scrollport width");
    assert_equals(f.scroller.clientHeight, 100, "calibration: scrollport height");
    const skipped = waitSkipped(t, f, result.events);
    f.subject.classList.add("auto");
    rect(f.scroller);
    await skipped;
    assert_true(result.events.at(-1).skipped && result.events.at(-1).trusted,
                "calibration: trusted skipped-state notification");
    if (c.change) f.table.classList.add("narrow");
    result.outerAfterMutation = rect(f.scroller);
    result.preScrollOffset = offset(f);
    assert_array_equals(result.outerAfterMutation, [0, 0, 100, 100], "calibration: outer-only mutation flush");
    assert_array_equals(result.preScrollOffset, [0, 0], "calibration: no pre-scroll movement");
    f.target.scrollIntoView(scrollOptions);
    result.immediateOffset = offset(f);
    const peer = fixture(c, c.change);
    t.add_cleanup(() => peer.scroller.remove());
    result.visible = {subject: rect(peer.subject), target: rect(peer.target), cells: peer.cells.map(rect)};
    peer.target.scrollIntoView(scrollOptions);
    result.visibleOffset = offset(peer);
    const width = c.change ? 80 : 160;
    assert_array_equals(result.visible.subject, [0, 8000, 600, 80], "calibration: unchanged explicit peer size");
    assert_array_equals(result.visible.target, [width, 8000, width, 40], "calibration: changed visible target");
    for (let i = 0; i < 3; ++i) {
      assert_array_equals(result.visible.cells[i], [width * i, 8000, width, 40], `calibration: changed visible cell ${i}`);
    }
    assert_array_equals(result.visibleOffset, [width, 8000], "calibration: visible start-aligned scroll");
    peer.scroller.remove();
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    result.settledOffset = offset(f);
    result.after = {target: rect(f.target), subject: rect(f.subject)};
    assert_array_equals(result.immediateOffset, [width, 8000], "first scroll uses current column geometry");
    assert_array_equals(result.settledOffset, [width, 8000], "scroll remains start-aligned after rendering");
    assert_array_equals(result.after.target, [0, 0, width, 40], "scrolled target rectangle");
    assert_array_equals(result.after.subject, [-width, 0, 600, 80], "subject dimensions remain fixed after relevance update");
  }, c.name);
}
