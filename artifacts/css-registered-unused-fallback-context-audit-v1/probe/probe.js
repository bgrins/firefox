"use strict";
const cases = [
  { id: "direct", css: "--x:5px;font-size:var(--x)", expected: "5px", calibration: true },
  { id: "valid-primary-no-fallback", css: "--known:5px;--x:var(--known);font-size:var(--x)", expected: "5px", calibration: true },
  { id: "valid-primary-px-fallback", css: "--known:5px;--x:var(--known,1px);font-size:var(--x)", expected: "5px", calibration: true },
  { id: "valid-primary-em-fallback", css: "--known:5px;--x:var(--known,1em);font-size:var(--x)", expected: "5px" },
  { id: "used-em-fallback-cycle", css: "--x:var(--missing,1em);font-size:var(--x)", expected: "19px", calibration: true },
  { id: "direct-em-cycle", css: "--x:1em;font-size:var(--x)", expected: "19px", calibration: true },
  { id: "inherited-provider-unused-em", parent: "--known:5px", css: "--x:var(--known,1em);font-size:var(--x)", expected: "5px" },
  { id: "number-unused-em", css: "--known:5;--n:var(--known,1em);font-size:calc(var(--n)*1px)", property: "--n", expected: "5px", calibration: true },
  { id: "universal-unused-em", css: "--known:5px;--u:var(--known,1em);font-size:var(--u)", property: "--u", expected: "5px", calibration: true },
  { id: "inherited-computed-length", parent: "--i:1em", css: "font-size:var(--i)", property: "--i", expected: "19px", calibration: true },
  { id: "provider-unused-em", css: "--known:var(--valid,1em);--valid:5px;--x:var(--known);font-size:var(--x)", expected: "5px" }
];
const rows = [];
for (const item of cases) {
  const parent = document.createElement("div");
  parent.style.cssText = "font-size:19px;" + (item.parent || "");
  const target = document.createElement("div");
  target.style.cssText = item.css;
  parent.append(target);
  document.body.append(parent);
  const style = getComputedStyle(target);
  rows.push({ ...item, observed: style.fontSize,
    computed: style.getPropertyValue(item.property || "--x").trim(),
    repeat: getComputedStyle(target).fontSize });
  parent.remove();
}
fetch("/result", { method: "POST", body: JSON.stringify({
  userAgent: navigator.userAgent, typedSupported: CSS.supports("font-size", "var(--x)"),
  registrationRules: [...document.styleSheets[0].cssRules].map(rule => rule.constructor.name), rows
}) });
