from pathlib import Path
p = Path(__file__).resolve().parent / 'wpt'
p.mkdir(exist_ok=True)
(p / 'attr-resolved-unit-dependencies.html').write_text('''<!doctype html>
<meta charset="utf-8">
<title>Relative units in resolved attribute and universal values</title>
<link rel="help" href="https://drafts.css-houdini.org/css-properties-values-api-1/#dependency-cycles">
<link rel="help" href="https://drafts.csswg.org/css-values-5/#attr-substitution">
<script src="/resources/testharness.js"></script>
<script src="/resources/testharnessreport.js"></script>
<style>:root { font-size: 19px; line-height: 29px; }</style>
<body>
<script>
CSS.registerProperty({name: "--summary-length", syntax: "<length>",
                      inherits: false, initialValue: "11px"});
CSS.registerProperty({name: "--summary-text", syntax: "<string>",
                      inherits: false, initialValue: '"initial"'});
CSS.registerProperty({name: "--summary-url", syntax: "<url>", inherits: false,
                      initialValue: 'url("https://example.invalid/initial")'});

function fixture(t, declarations, attribute) {
  const parent = document.createElement("div");
  parent.style.cssText = "font-size: 23px; line-height: 37px";
  const target = document.createElement("div");
  target.style.cssText = "width: var(--summary-length); " + declarations;
  if (attribute !== undefined) {
    target.setAttribute("a", attribute);
  }
  parent.append(target);
  document.body.append(parent);
  t.add_cleanup(() => parent.remove());
  assert_equals(getComputedStyle(parent).fontSize, "23px", "parent calibration");
  return getComputedStyle(target);
}

const attribute = "--summary-length: attr(a type(<length>)); ";
const chain = "--raw: var(--unit); --summary-length: var(--raw); ";
const cases = [
  ["Resolved attribute font cycle", attribute + "font-size: var(--summary-length)",
   "1em", "11px", "23px"],
  ["Substituted universal font cycle", "--unit: 1em; " + chain +
   "font-size: var(--summary-length)", undefined, "11px", "23px"],
  ["Resolved attribute font ordering", attribute + "font-size: 17px",
   "1em", "17px", "17px"],
  ["Literal attribute control", attribute + "font-size: var(--summary-length)",
   "13px", "13px", "13px"],
  ["Literal registered cycle control", "--summary-length: 1em; " +
   "font-size: var(--summary-length)", undefined, "11px", "23px"],
  ["Escaped attribute unit", attribute + "font-size: var(--summary-length)",
   String.raw`1e\\6d`, "11px", "23px"],
  ["Escaped universal unit", String.raw`--unit: 1\\65 m; ` + chain +
   "font-size: var(--summary-length)", undefined, "11px", "23px"],
  ["Nested attribute calculation", attribute + "font-size: var(--summary-length)",
   "calc(1px + min(1em, 100px))", "11px", "23px"],
  ["Nested universal calculation", "--unit: calc(1px + min(1em, 100px)); " +
   chain + "font-size: var(--summary-length)", undefined, "11px", "23px"],
  ["Attribute line-height ordering", attribute + "font-size: 17px; line-height: 31px",
   "1lh", "31px", "17px"],
  ["Universal line-height ordering", "--unit: 1lh; " + chain +
   "font-size: 17px; line-height: 31px", undefined, "31px", "17px"],
  ["Attribute root font unit", attribute + "font-size: var(--summary-length)",
   "1rem", "19px", "19px"],
  ["Attribute root line-height unit", attribute + "font-size: var(--summary-length)",
   "1rlh", "29px", "29px"],
  ["Universal root line-height unit", "--unit: 1rlh; " + chain +
   "font-size: var(--summary-length)", undefined, "29px", "29px"],
  ["Comment text is not a font dependency", attribute +
   "font-size: var(--summary-length)", "calc(13px /* 1em 1lh */)", "13px", "13px"],
  ["Token separator does not create a dimension", "--unit: 1/**/em; " + chain +
   "font-size: var(--summary-length)", undefined, "11px", "11px"],
];
for (const [name, declarations, value, length, font] of cases) {
  test(t => {
    const computed = fixture(t, declarations, value);
    assert_equals(computed.getPropertyValue("--summary-length").trim(), length,
                  "registered length");
    assert_equals(computed.fontSize, font, "font size");
    assert_equals(computed.width, length, "width");
  }, name);
}

test(t => {
  const parent = document.createElement("div");
  parent.style.cssText = "font-size: 23px; --unit: 1em; --raw: var(--unit)";
  const target = document.createElement("div");
  target.style.cssText = "font-size: 17px; --summary-length: var(--raw); width: var(--summary-length)";
  parent.append(target);
  document.body.append(parent);
  t.add_cleanup(() => parent.remove());
  assert_equals(getComputedStyle(parent).fontSize, "23px", "parent calibration");
  const computed = getComputedStyle(target);
  assert_equals(computed.getPropertyValue("--summary-length").trim(), "17px", "registered length");
  assert_equals(computed.fontSize, "17px", "font size");
  assert_equals(computed.width, "17px", "width");
}, "Inherited substituted universal value uses the consuming element's font");

for (const text of ['"1em"', '"var(--x, 1lh)"']) {
  test(t => {
    const computed = fixture(t,
      "--summary-text: attr(a type(<string>)); font-size: var(--summary-text)", text);
    assert_equals(computed.getPropertyValue("--summary-text").trim(), text,
                  "registered string");
    assert_equals(computed.fontSize, "23px", "invalid font value inherits");
  }, "String contents are not dependencies: " + text);
}

for (const url of ["url(1em)", 'url("1lh")']) {
  test(t => {
    const computed = fixture(t, "--unit: " + url +
      "; --raw: var(--unit); --summary-url: var(--raw); font-size: var(--summary-url)");
    const path = url === "url(1em)" ? "1em" : "1lh";
    assert_equals(computed.getPropertyValue("--summary-url").trim(),
                  'url("' + new URL(path, location.href).href + '")', "registered URL");
    assert_equals(computed.fontSize, "23px", "invalid font value inherits");
  }, "URL contents are not dependencies: " + url);
}
</script>
''')
