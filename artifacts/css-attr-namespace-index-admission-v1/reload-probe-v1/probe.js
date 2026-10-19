"use strict";
function runAttributeReloadProbe() {
  const definitions = [
  [
    "repeat-cycle",
    "attr(x type(*), 13px) attr(x type(*), 37px)",
    {
      "x": "attr(x type(*))"
    },
    "13px 37px",
    "13px",
    "37px",
    true
  ],
  [
    "single-cycle",
    "attr(x type(*), 13px)",
    {
      "x": "attr(x type(*))"
    },
    "13px",
    "13px",
    "13px",
    false
  ],
  [
    "repeat-constrained-cycle",
    "attr(x type(<length>), 13px) attr(x type(<length>), 37px)",
    {
      "x": "attr(x type(*))"
    },
    "13px 37px",
    "13px",
    "37px",
    false
  ],
  [
    "repeat-invalid",
    "attr(x type(*), 13px) attr(x type(*), 37px)",
    {
      "x": "var(--missing)"
    },
    "13px 37px",
    "13px",
    "37px",
    true
  ],
  [
    "single-invalid",
    "attr(x type(*), 13px)",
    {
      "x": "var(--missing)"
    },
    "13px",
    "13px",
    "13px",
    false
  ],
  [
    "repeat-literal",
    "attr(x type(*), 13px) attr(x type(*), 37px)",
    {
      "x": "19px"
    },
    "19px 19px",
    "19px",
    "19px",
    false
  ],
  [
    "distinct-cycles",
    "attr(x type(*), 13px) attr(y type(*), 37px)",
    {
      "x": "attr(x type(*))",
      "y": "attr(y type(*))"
    },
    "13px 37px",
    "13px",
    "37px",
    false
  ],
  [
    "repeat-two-node-cycle",
    "attr(x type(*), 13px) attr(x type(*), 37px)",
    {
      "x": "attr(y type(*))",
      "y": "attr(x type(*))"
    },
    "13px 37px",
    "13px",
    "37px",
    true
  ],
  [
    "same-cycle-value-different-names",
    "attr(x type(*), 13px) attr(y type(*), 37px)",
    {
      "x": "attr(x type(*))",
      "y": "attr(x type(*))"
    },
    "13px 37px",
    "13px",
    "37px",
    true
  ],
  [
    "independent-declarations",
    "attr(x type(*), 13px)",
    {
      "x": "attr(x type(*))"
    },
    "13px",
    "13px",
    "37px",
    false
  ]
];
  const fixture = document.getElementById("fixture");
  const fragment = document.createDocumentFragment();
  for (const [id, , attributes] of definitions) {
    const target = document.createElement("div");
    target.id = id;
    target.className = "target";
    for (const [name, value] of Object.entries(attributes)) {
      target.setAttribute(name, value);
    }
    fragment.append(target);
  }
  fixture.append(fragment);
  const sheet = document.getElementById("probe-sheet").sheet;
  const specified = Object.fromEntries(Array.from(sheet.cssRules)
    .filter(rule => rule.selectorText?.startsWith("#") && rule.style.getPropertyValue("--out").trim())
    .map(rule => [rule.selectorText.slice(1), rule.style.getPropertyValue("--out").trim()]));
  return {
    support: CSS.supports("margin", "attr(x type(*), 13px)"),
    fixtureWidth: getComputedStyle(fixture).width,
    rows: definitions.map(([id, declaration, attributes, custom, top, right, predictedFailure]) => {
      const target = document.getElementById(id);
      const computed = getComputedStyle(target);
      const second = id === "independent-declarations" ? "37px" : "";
      const actual = {second: computed.getPropertyValue("--second").trim(), custom: computed.getPropertyValue("--out").trim().replace(/\s+/g, " "),
        top: computed.marginTop, right: computed.marginRight};
      return {id, expected: {custom, top, right, second}, actual, predictedFailure,
        pass: actual.second === second && actual.custom === custom && actual.top === top && actual.right === right,
        declaration, specified: specified[id],
        attributes: Object.fromEntries(Object.keys(attributes).map(name => [name, target.getAttribute(name)])),
        missingCustom: computed.getPropertyValue("--missing"), width: computed.width};
    }),
  };
}
