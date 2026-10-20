"use strict";
const rows = [];
const query = {
  bounding(node) {
    const rect = node.getBoundingClientRect();
    return [rect.width, rect.height];
  },
  offset: node => [node.offsetWidth, node.offsetHeight],
};

function create(configuration, inserted) {
  const host = document.createElement("div");
  host.className = "host";
  const subject = document.createElement("div");
  subject.className = `subject ${configuration.mode}`;
  const item = document.createElement("div");
  item.className = "item";
  let target = item;
  if (configuration.nested) {
    target = document.createElement("div");
    target.className = "nested";
    item.append(target);
  }
  subject.append(item);
  const added = document.createElement("div");
  added.className = "added";
  if (inserted) {
    subject[configuration.insertion](added);
  }
  host.append(subject);
  document.body.append(host);
  return {host, subject, item, target, added};
}

function outerFlush(fixture) {
  return [fixture.subject.getClientRects().length,
    fixture.subject.scrollWidth, fixture.subject.scrollHeight];
}

try {
  if (!CSS.supports("content-visibility", "hidden")) {
    throw new Error("content-visibility: hidden is unsupported");
  }
  for (const nested of [false, true]) {
    for (const insertion of ["append", "prepend"]) {
      for (const mode of ["shrink", "no-shrink", "zero-sibling"]) {
        for (const hidden of [false, true]) {
          for (const api of Object.keys(query)) {
            const configuration = {nested, insertion, mode, hidden, api};
            const fixture = create(configuration, false);
            const record = {...configuration, stages: []};
            rows.push(record);
            try {
              for (const phase of ["warm", "visibility", "insert", "remove", "show"]) {
                if (phase === "visibility") fixture.subject.classList.toggle("hidden", hidden);
                if (phase === "insert") fixture.subject[insertion](fixture.added);
                if (phase === "remove") fixture.added.remove();
                if (phase === "show") fixture.subject.classList.remove("hidden");
                const outer = outerFlush(fixture);
                const first = query[api](fixture.target);
                const second = query[api](fixture.target);
                const third = query[api](fixture.target);
                const reference = create(configuration, phase === "insert");
                let visible;
                try {
                  outerFlush(reference);
                  visible = query[api](reference.target);
                } finally {
                  reference.host.remove();
                }
                record.stages.push({phase, outer, first, second, third, visible,
                  expected: [phase === "insert" && mode === "shrink" ? 50 : 100, 32]});
              }
            } finally {
              fixture.host.remove();
            }
          }
        }
      }
    }
  }
  fetch("/result", {method: "POST", body: JSON.stringify({rows, userAgent: navigator.userAgent})});
} catch (error) {
  fetch("/result", {method: "POST", body: JSON.stringify({error: String(error), stack: error.stack, rows})});
}
