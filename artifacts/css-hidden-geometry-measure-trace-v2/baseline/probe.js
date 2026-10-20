"use strict";
const rows = [];
const queries = {
  bounding: n => { const r = n.getBoundingClientRect(); return [r.width, r.height]; },
  rects: n => [...n.getClientRects()].map(r => [r.width, r.height]),
  offset: n => [n.offsetWidth, n.offsetHeight],
  scroll: n => [n.scrollWidth, n.scrollHeight],
};
try {
  for (const columns of [false, true]) {
    for (const flex of [false, true]) {
      for (const initiallyHidden of [false, true]) {
        for (const [api, query] of Object.entries(queries)) {
          const host = document.createElement("div");
          host.className = `host ${columns ? "columns" : ""}`;
          const subject = document.createElement("div");
          subject.className = `subject ${flex ? "flex" : ""} ${initiallyHidden ? "hidden" : ""}`;
          const target = document.createElement("div");
          target.className = "target";
          subject.append(target);
          host.append(subject);
          document.body.append(host);
          const stages = [];
          for (const phase of ["initial", "hide", "append", "append-again", "show"]) {
            if (phase === "hide") subject.classList.add("hidden");
            if (phase.startsWith("append")) {
              const added = document.createElement("div");
              added.className = "added";
              subject.append(added);
            }
            if (phase === "show") subject.classList.remove("hidden");
            const outer = [subject.getClientRects().length, subject.scrollWidth, subject.scrollHeight];
            const first = query(target);
            const second = query(target);
            const third = query(target);
            stages.push({phase, outer, first, second, third});
          }
          rows.push({columns, flex, initiallyHidden, api, stages});
          host.remove();
        }
      }
    }
  }
  fetch("/result", {method: "POST", body: JSON.stringify({rows, userAgent: navigator.userAgent})});
} catch (error) {
  fetch("/result", {method: "POST", body: JSON.stringify({error: String(error), stack: error.stack, rows})});
}
