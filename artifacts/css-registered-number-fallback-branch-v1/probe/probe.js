"use strict";
const cases = [
  {
    "id": "direct-number",
    "css": "--n:5",
    "expected": "5px",
    "calibration": true
  },
  {
    "id": "ready-no-fallback",
    "css": "--ready:5;--n:var(--ready)",
    "expected": "5px",
    "calibration": true
  },
  {
    "id": "ready-number-fallback",
    "css": "--ready:5;--n:var(--ready,2)",
    "expected": "5px",
    "calibration": true
  },
  {
    "id": "ready-px-fallback",
    "css": "--ready:5;--n:var(--ready,1px)",
    "expected": "5px",
    "calibration": true
  },
  {
    "id": "ready-em-fallback",
    "css": "--ready:5;--n:var(--ready,1em)",
    "expected": "5px",
    "calibration": false
  },
  {
    "id": "ready-lh-fallback",
    "css": "--ready:5;--n:var(--ready,1lh)",
    "expected": "5px",
    "calibration": false
  },
  {
    "id": "ready-ex-fallback",
    "css": "--ready:5;--n:var(--ready,1ex)",
    "expected": "5px",
    "calibration": false
  },
  {
    "id": "ready-nested-em-fallback",
    "css": "--ready:5;--n:var(--ready,var(--missing,1em))",
    "expected": "5px",
    "calibration": false
  },
  {
    "id": "missing-number-fallback",
    "css": "--n:var(--missing,5)",
    "expected": "5px",
    "calibration": true
  },
  {
    "id": "missing-em-fallback",
    "css": "--n:var(--missing,1em)",
    "expected": "3px",
    "calibration": false
  },
  {
    "id": "wrong-primary-unused-em",
    "css": "--wrong:red;--n:var(--wrong,1em)",
    "expected": "3px",
    "calibration": false
  },
  {
    "id": "direct-invalid-em",
    "css": "--n:1em",
    "expected": "3px",
    "calibration": true
  },
  {
    "id": "inherited-ready-unused-em",
    "css": "--n:var(--ready,1em)",
    "expected": "5px",
    "calibration": false,
    "parent": "--ready:5"
  },
  {
    "id": "provider-contained-unused-em",
    "css": "--ready:5;--middle:var(--ready,1em);--n:var(--middle)",
    "expected": "5px",
    "calibration": true
  }
];
const rows = [];
for (const item of cases) {
  const parent = document.createElement("div");
  parent.style.cssText = "font-size:19px;line-height:23px;" + (item.parent || "");
  const target = document.createElement("div");
  target.style.cssText = item.css + ";font-size:calc(var(--n)*1px)";
  parent.append(target);
  document.body.append(parent);
  const style = getComputedStyle(target);
  rows.push({...item, observed:style.fontSize, computed:style.getPropertyValue("--n").trim(), repeat:getComputedStyle(target).fontSize});
  parent.remove();
}
fetch("/result", {method:"POST", body:JSON.stringify({userAgent:navigator.userAgent,registrationRules:[...document.styleSheets[0].cssRules].map(rule=>rule.constructor.name),rows})});
