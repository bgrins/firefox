"use strict";

const occurrenceResults = [];
const occurrenceDeclarations = `
  margin-left: 17px;
  margin-right: 19px;
  margin-inline-start: var(--occurrence-value, revert-rule) !important;
`;

function addStyle(document, parent, text) {
  const style = document.createElement("style");
  style.textContent = text;
  parent.append(style);
}

function phaseMarker(record) {
  if (typeof window.dump === "function") {
    window.dump(`CSS_OCCURRENCE_PHASE_V1 ${JSON.stringify(record)}\n`);
  }
}

function loadSheet(t, document, parent, name) {
  return new Promise((resolve, reject) => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = new URL(`resources/${name}.css`, location.href);
    const timeout = t.step_timeout(() => reject(new Error(`Loading ${name} timed out`)), 8000);
    t.add_cleanup(() => clearTimeout(timeout));
    link.onload = () => {
      clearTimeout(timeout);
      resolve(link);
    };
    link.onerror = () => {
      clearTimeout(timeout);
      reject(new Error(`Loading ${name} failed`));
    };
    parent.append(link);
  });
}

async function createCase(t, family, direction, independent) {
  phaseMarker({family, direction, independent, event: "begin-setup"});
  const frame = document.createElement("iframe");
  frame.srcdoc = `<!doctype html><meta charset="utf-8"><body dir="${direction}">
    <div id="outer"><div id="middle"><div id="inner">
      <div id="target" class="target other">target</div>
    </div></div></div>`;
  t.add_cleanup(() => frame.remove());
  await new Promise((resolve, reject) => {
    const timeout = t.step_timeout(() => reject(new Error("Frame load timed out")), 8000);
    t.add_cleanup(() => clearTimeout(timeout));
    frame.onload = () => {
      clearTimeout(timeout);
      resolve();
    };
    document.body.append(frame);
  });
  const doc = frame.contentDocument;
  addStyle(doc, doc.head, `
    .target { writing-mode: horizontal-tb; margin-left: 11px; margin-right: 13px; }
    .target[data-value="small"] { --occurrence-value: 29px; }
    .target[data-value="large"] { --occurrence-value: 43px; }
  `);
  if (family === "selector-list") {
    const rules = independent
      ? `.target { ${occurrenceDeclarations} } #target { ${occurrenceDeclarations} }`
      : `.target, #target { ${occurrenceDeclarations} }`;
    addStyle(doc, doc.head, rules);
    addStyle(doc, doc.head, ".target.other { margin-left: 31px; margin-right: 37px; }");
  } else {
    const scoped = family === "implicit-scope";
    const stem = scoped ? "occurrence-scoped" : "occurrence-shared";
    const firstParent = scoped ? doc.getElementById("outer") : doc.head;
    const lastParent = scoped ? doc.getElementById("inner") : doc.head;
    await loadSheet(t, doc, firstParent, stem + (independent ? "-independent-a" : ""));
    const competitor = "#target { margin-left: 31px; margin-right: 37px; }";
    addStyle(doc, scoped ? doc.getElementById("middle") : doc.head,
      scoped ? `@scope { ${competitor} }` : competitor);
    await loadSheet(t, doc, lastParent, stem + (independent ? "-independent-b" : ""));
  }
  phaseMarker({family, direction, independent, event: "end-setup"});
  return {frame, target: doc.getElementById("target"), independent};
}

function readMargins(context, metadata) {
  const label = {...metadata, independent: context.independent};
  phaseMarker({...label, event: "begin-read"});
  const style = context.frame.contentWindow.getComputedStyle(context.target);
  const values = [style.marginLeft, style.marginRight];
  phaseMarker({...label, event: "end-read", values});
  return values;
}

for (const family of ["selector-list", "cache-clone", "implicit-scope"]) {
  for (const direction of ["ltr", "rtl"]) {
    promise_test(async t => {
      assert_true(CSS.supports("margin-left", "revert-rule"), "revert-rule support is required");
      const shared = await createCase(t, family, direction, false);
      const independent = await createCase(t, family, direction, true);
      for (const [phase, value] of [
        ["initial-rollback", null],
        ["small-value", "small"],
        ["large-value", "large"],
        ["return-to-rollback", null],
      ]) {
        for (const context of [shared, independent]) {
          if (value === null) {
            context.target.removeAttribute("data-value");
          } else {
            context.target.setAttribute("data-value", value);
          }
        }
        const amount = value === "small" ? "29px" : value === "large" ? "43px" : null;
        const expected = direction === "ltr" ? [amount ?? "31px", "19px"] : ["17px", amount ?? "37px"];
        const metadata = {family, direction, phase};
        const actual = readMargins(shared, metadata);
        const control = readMargins(independent, metadata);
        occurrenceResults.push({...metadata, expected, actual, control});
        assert_array_equals(actual, control, `${phase}: shared and independent sources agree`);
        assert_array_equals(control, expected, `${phase}: independent source result`);
        assert_array_equals(actual, expected, `${phase}: repeated source result`);
      }
    }, `${family}: ${direction} mixed-importance aliases survive receiver var mutation`);
  }
}
