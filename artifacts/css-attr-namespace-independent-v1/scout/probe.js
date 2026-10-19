"use strict";

function runAttrNamespaceProbe() {
  const definitions = [
    ["typed-width-first", "13px", "37px", "37px", "37px"],
    ["typed-height-first", "13px", "37px", "13px", "13px"],
    ["only-a", "13px", "7px", "13px", "7px"],
    ["only-b", "5px", "37px", "5px", "37px"],
    ["distinct-local-names", "13px", "37px", "13px", "37px"],
    ["same-qualified-name", "13px", "13px", "13px", "13px"],
    ["numeric-units", "13px", "37px", "13px", "37px"],
    ["null-and-named-distinct", "13px", "37px", "13px", "37px"],
  ];
  const fixture = document.getElementById("fixture");
  for (const [id] of definitions) {
    const target = document.createElement("div");
    target.id = id;
    target.className = "target";
    target.setAttributeNS("urn:attr-observer:a", "a:x", "13px");
    target.setAttributeNS("urn:attr-observer:b", "b:x", "37px");
    target.setAttributeNS("urn:attr-observer:b", "b:y", "37px");
    target.setAttributeNS("urn:attr-observer:a", "a:n", "13");
    target.setAttributeNS("urn:attr-observer:b", "b:n", "37");
    target.setAttribute("z", "13px");
    fixture.append(target);
  }
  const sheet = document.getElementById("probe-sheet").sheet;
  const declarations = Object.fromEntries(Array.from(sheet.cssRules)
    .filter(rule => rule.selectorText?.startsWith("#"))
    .map(rule => [rule.selectorText.slice(1), rule.style.cssText]));
  const rows = definitions.map(([id, width, height, nativeWidth, nativeHeight]) => {
    const target = document.getElementById(id);
    const computed = getComputedStyle(target);
    return {
      id,
      expected: {width, height},
      sourcePrediction: {width: nativeWidth, height: nativeHeight},
      actual: {width: computed.width, height: computed.height},
      pass: computed.width === width && computed.height === height,
      declaration: declarations[id] ?? "",
      attributes: {
        aX: target.getAttributeNS("urn:attr-observer:a", "x"),
        bX: target.getAttributeNS("urn:attr-observer:b", "x"),
        bY: target.getAttributeNS("urn:attr-observer:b", "y"),
        aN: target.getAttributeNS("urn:attr-observer:a", "n"),
        bN: target.getAttributeNS("urn:attr-observer:b", "n"),
        nullZ: target.getAttributeNS(null, "z"),
      },
    };
  });
  return {
    support: {
      typed: CSS.supports("width", "attr(x type(<length>), 5px)"),
      unit: CSS.supports("width", "attr(x px, 5px)"),
      namespaceRules: Array.from(sheet.cssRules)
        .filter(rule => rule.type === CSSRule.NAMESPACE_RULE).map(rule => rule.cssText),
    },
    fixtureWidth: getComputedStyle(fixture).width,
    rows,
  };
}
