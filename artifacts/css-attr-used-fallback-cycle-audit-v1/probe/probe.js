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
];

const rows = cases.map(item => {
  const element = document.createElement("div");
  if (item.foo !== undefined) {
    element.setAttribute("data-foo", item.foo);
  }
  for (const [name, value] of item.declarations) {
    element.style.setProperty(name, value);
  }
  element.style.color = "var(--x, green)";
  document.body.append(element);
  const style = getComputedStyle(element);
  const observed = style.getPropertyValue("--x").trim();
  const other = style.getPropertyValue("--y").trim();
  const color = style.color;
  const repeat = getComputedStyle(element).getPropertyValue("--x").trim();
  element.remove();
  const row = document.createElement("tr");
  for (const value of [item.id, observed, color, item.expected || "invalid; green"]) {
    const cell = document.createElement("td");
    const code = document.createElement("code");
    code.textContent = value;
    cell.append(code);
    row.append(cell);
  }
  document.getElementById("results").append(row);
  return {...item, observed, other, color, repeat};
});

const result = {userAgent: navigator.userAgent, typedSupported: CSS.supports("width", "attr(data-foo type(<length>))"), rows};
window.probeResult = result;
if (location.hostname === "127.0.0.1") {
  fetch("/result", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(result)});
}
