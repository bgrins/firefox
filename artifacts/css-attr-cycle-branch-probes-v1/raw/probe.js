const cases = [
  {id: "raw-literal", declaration: "attr(data-foo)", foo: "hello", expected: '"hello"', calibration: true},
  {id: "typed-literal", declaration: "attr(data-foo type(*), abc)", foo: "hello", expected: "hello", calibration: true},
  {id: "typed-self-bare", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-foo)", expected: '"attr(data-foo)"'},
  {id: "typed-self-raw", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-foo raw-string)", expected: '"attr(data-foo raw-string)"'},
  {id: "genuine-typed-self", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-foo type(*))", expected: "abc", calibration: true},
  {id: "nested-bare", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-bar type(*), fallback)", bar: "attr(data-foo) attr(data-bar)", expected: '"attr(data-bar type(*), fallback)" "attr(data-foo) attr(data-bar)"'},
  {id: "nested-raw", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-bar type(*), fallback)", bar: "attr(data-foo raw-string) attr(data-bar raw-string)", expected: '"attr(data-bar type(*), fallback)" "attr(data-foo raw-string) attr(data-bar raw-string)"'},
  {id: "bare-other", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-bar)", bar: "hello", expected: '"hello"', calibration: true},
  {id: "typed-string-self-bare", declaration: "attr(data-foo type(<string>), abc)", foo: "attr(data-foo)", expected: '"attr(data-foo)"'},
  {id: "bare-missing", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-missing)", expected: '""', calibration: true},
  {id: "taken-bare-fallback-cycle", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-missing, attr(data-foo type(*)))", expected: "abc", calibration: true},
  {id: "unused-bare-fallback-cycle", declaration: "attr(data-foo type(*), abc)", foo: "attr(data-bar, attr(data-foo type(*)))", bar: "hello", expected: '"hello"', calibration: true},
  {id: "quoted-function-control", declaration: "attr(data-foo type(*), abc)", foo: '"attr(data-foo)" "attr(data-bar)"', expected: '"attr(data-foo)" "attr(data-bar)"', calibration: true},
];

const rows = cases.map(item => {
  const element = document.createElement("div");
  element.setAttribute("data-foo", item.foo);
  if (item.bar !== undefined) {
    element.setAttribute("data-bar", item.bar);
  }
  element.style.setProperty("--x", item.declaration);
  document.body.append(element);
  const observed = getComputedStyle(element).getPropertyValue("--x").trim();
  const repeat = getComputedStyle(element).getPropertyValue("--x").trim();
  element.remove();
  const row = document.createElement("tr");
  for (const value of [item.id, observed, item.expected]) {
    const cell = document.createElement("td");
    const code = document.createElement("code");
    code.textContent = value;
    cell.append(code);
    row.append(cell);
  }
  document.getElementById("results").append(row);
  return {...item, observed, repeat};
});

const result = {userAgent: navigator.userAgent, typedSupported: CSS.supports("width", "attr(data-foo type(<length>))"), rows};
window.probeResult = result;
if (location.hostname === "127.0.0.1") {
  fetch("/result", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(result)});
}
