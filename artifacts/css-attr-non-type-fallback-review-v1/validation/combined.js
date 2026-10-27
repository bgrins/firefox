
const cases = [
  {id: "missing-bare-self", declarations: [["--x", "attr(data-missing, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "missing-raw-self", declarations: [["--x", "attr(data-missing raw-string, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "invalid-number-self", foo: "nope", declarations: [["--x", "attr(data-foo number, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "invalid-unit-self", foo: "nope", declarations: [["--x", "attr(data-foo px, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "missing-unit-self", declarations: [["--x", "attr(data-missing px, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "missing-bare-mutual", declarations: [["--x", "attr(data-missing, var(--y, red))"], ["--y", "var(--x, blue)"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "missing-bare-mutual-reordered", declarations: [["--y", "var(--x, blue)"], ["--x", "attr(data-missing, var(--y, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "direct-var-self", declarations: [["--x", "var(--x, red)"]], expected: "", expectedColor: "rgb(0, 128, 0)", calibration: true},
  {id: "missing-typed-self", declarations: [["--x", "attr(data-missing type(*), var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)", calibration: true},
  {id: "missing-bare-acyclic", declarations: [["--x", "attr(data-missing, red)"]], expected: "red", expectedColor: "rgb(255, 0, 0)", calibration: true},
  {id: "missing-bare-ready-provider", declarations: [["--x", "attr(data-missing, var(--ready, red))"], ["--ready", "blue"]], expected: "blue", expectedColor: "rgb(0, 0, 255)", calibration: true},
  {id: "present-bare-unused-self", foo: "red", declarations: [["--x", "attr(data-foo, var(--x, blue))"]], expected: '"red"', expectedColor: "rgb(0, 0, 0)", calibration: true},
  {id: "valid-number-unused-self", foo: "5", declarations: [["--x", "attr(data-foo number, var(--x, red))"]], expected: "5", expectedColor: "rgb(0, 0, 0)", calibration: true},
  {id: "empty-bare-primary", foo: "", declarations: [["--x", "attr(data-foo, var(--x, red))"]], expected: '""', expectedColor: "rgb(0, 0, 0)"},
  {id: "empty-raw-primary", foo: "", declarations: [["--x", "attr(data-foo raw-string, var(--x, red))"]], expected: '""', expectedColor: "rgb(0, 0, 0)"},
  {id: "empty-number-primary", foo: "", declarations: [["--x", "attr(data-foo number, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "whitespace-number-primary", foo: " \t ", declarations: [["--x", "attr(data-foo number, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "number-with-whitespace", foo: " \t5 \n", declarations: [["--x", "attr(data-foo number, var(--x, red))"]], expected: "5", expectedColor: "rgb(0, 0, 0)"},
  {id: "unit-with-whitespace", foo: " \t5 \n", declarations: [["--x", "attr(data-foo px, var(--x, red))"]], expected: "5px", expectedColor: "rgb(0, 0, 0)"},
  {id: "number-extra-token", foo: "5 6", declarations: [["--x", "attr(data-foo number, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "number-dimension-token", foo: "5px", declarations: [["--x", "attr(data-foo number, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "namespaced-missing-with-null-present", foo: "red", declarations: [["--x", "attr(a|data-foo, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "namespaced-raw-primary", namespaced: "red", declarations: [["--x", "attr(a|data-foo, var(--x, red))"]], expected: '"red"', expectedColor: "rgb(0, 0, 0)"},
  {id: "namespaced-valid-number", foo: "nope", namespaced: " 5 ", declarations: [["--x", "attr(a|data-foo number, var(--x, red))"]], expected: "5", expectedColor: "rgb(0, 0, 0)"},
  {id: "namespaced-invalid-number", foo: "5", namespaced: "nope", declarations: [["--x", "attr(a|data-foo number, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "unknown-namespace", foo: "red", declarations: [["--x", "attr(unknown|data-foo, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
  {id: "raw-function-text", foo: "var(--x)", declarations: [["--x", "attr(data-foo, var(--x, red))"]], expected: '"var(--x)"', expectedColor: "rgb(0, 0, 0)"},
  {id: "same-attribute-different-syntax", foo: "red", declarations: [["--x", "attr(data-foo raw-string, var(--x)) attr(data-foo number, var(--x, red))"]], expected: "", expectedColor: "rgb(0, 128, 0)"},
];

for (const [index, item] of cases.entries()) {
  test(t => {
    const target = document.createElement("div");
    target.id = `target-${index}`;
    t.add_cleanup(() => target.remove());
    if (item.foo !== undefined) {
      target.setAttribute("data-foo", item.foo);
    }
    if (item.namespaced !== undefined) {
      target.setAttributeNS("urn:attr-fallback", "a:data-foo", item.namespaced);
    }
    const style = document.createElement("style");
    t.add_cleanup(() => style.remove());
    const declarations = item.declarations.map(([name, value]) => `${name}: ${value}`).join(";");
    style.textContent = `@namespace a "urn:attr-fallback"; #${target.id} { ${declarations}; color: var(--x, green); }`;
    document.head.append(style);
    const rule = style.sheet.cssRules[1];
    for (const [name] of item.declarations) {
      assert_not_equals(rule.style.getPropertyValue(name), "", "Declaration parsed");
    }
    document.body.append(target);
    const computed = getComputedStyle(target);
    assert_equals(computed.getPropertyValue("--x").trim(), item.expected, "Custom property");
    assert_equals(computed.color, item.expectedColor, "Consuming property");
    if (item.id.startsWith("missing-bare-mutual")) {
      assert_equals(computed.getPropertyValue("--y").trim(), "", "Other cycle participant");
    }
  }, item.id);
}

for (const syntax of ["", "number"]) {
  test(t => {
    const target = document.createElement("div");
    t.add_cleanup(() => target.remove());
    target.style.cssText = `--x: attr(data-foo ${syntax}, var(--x, red)); color: var(--x, green)`;
    document.body.append(target);
    const check = expected => {
      assert_equals(getComputedStyle(target).getPropertyValue("--x").trim(), expected);
      assert_equals(getComputedStyle(target).color,
                    expected === "" ? "rgb(0, 128, 0)" : "rgb(0, 0, 0)");
    };
    check("");
    target.setAttribute("data-foo", "5");
    check(syntax ? "5" : '"5"');
    target.setAttribute("data-foo", "");
    check(syntax ? "" : '""');
    target.removeAttribute("data-foo");
    check("");
  }, `Attribute mutation updates ${syntax || "bare"} fallback cycle edges`);
}

CSS.registerProperty({
  name: "--non-type-edge-length",
  syntax: "<length>",
  inherits: false,
  initialValue: "11px",
});
const nonCustomCases = [
  {
    name: "Used non-type font-size fallback participates in a registered length cycle",
    declarations: "--non-type-edge-length: 1em; font-size: attr(data-size px, var(--non-type-edge-length))",
    property: "font-size",
    attribute: null,
    expected: {"--non-type-edge-length": "11px", "font-size": "23px", "line-height": "31px", width: "11px"},
  },
  {
    name: "Valid non-type font-size primary excludes a cyclic fallback",
    declarations: "--non-type-edge-length: 1em; font-size: attr(data-size px, var(--non-type-edge-length))",
    property: "font-size",
    attribute: "13",
    expected: {"--non-type-edge-length": "13px", "font-size": "13px", "line-height": "31px", width: "13px"},
  },
  {
    name: "Used non-type line-height fallback participates in a registered length cycle",
    declarations: "--non-type-edge-length: 1lh; line-height: attr(data-size px, var(--non-type-edge-length))",
    property: "line-height",
    attribute: "nope",
    expected: {"--non-type-edge-length": "11px", "font-size": "23px", "line-height": "31px", width: "11px"},
  },
  {
    name: "Valid non-type line-height primary excludes a cyclic fallback",
    declarations: "--non-type-edge-length: 1lh; line-height: attr(data-size px, var(--non-type-edge-length))",
    property: "line-height",
    attribute: "13",
    expected: {"--non-type-edge-length": "13px", "font-size": "23px", "line-height": "13px", width: "13px"},
  },
];
for (const item of nonCustomCases) {
  test(t => {
    const parent = document.createElement("div");
    t.add_cleanup(() => parent.remove());
    parent.style.cssText = "font-size: 23px; line-height: 31px";
    const target = document.createElement("div");
    target.style.cssText = "width: var(--non-type-edge-length); " + item.declarations;
    if (item.attribute !== null) {
      target.setAttribute("data-size", item.attribute);
    }
    assert_not_equals(target.style.getPropertyValue("--non-type-edge-length"), "", "Custom declaration parsed");
    assert_not_equals(target.style.getPropertyValue(item.property), "", "Prioritary declaration parsed");
    parent.append(target);
    document.body.append(parent);
    const computed = getComputedStyle(target);
    for (const [property, expected] of Object.entries(item.expected)) {
      assert_equals(computed.getPropertyValue(property).trim(), expected, property);
    }
  }, item.name);
}
