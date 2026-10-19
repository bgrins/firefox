
const target = "--enumeration-target";
const sentinel = "--enumeration-sentinel";

function fixture(t, parentValue) {
  const parent = document.createElement("div");
  const child = document.createElement("div");
  const reference = document.createElement("div");
  if (parentValue !== null) parent.style.setProperty(target, parentValue);
  parent.style.setProperty(sentinel, "sentinel");
  parent.append(child);
  document.body.append(parent, reference);
  t.add_cleanup(() => { parent.remove(); reference.remove(); });
  assert_equals(getComputedStyle(parent).getPropertyValue(target), parentValue ?? "", "Parent prerequisite");
  assert_array_equals(Array.from(getComputedStyle(reference)).filter(name => name.startsWith("--")), [], "No ambient custom properties");
  return { child, reference };
}

function check(child, reference, value, present) {
  const style = getComputedStyle(child);
  const names = Array.from(style).filter(name => name.startsWith("--")).sort();
  const expected = present ? [sentinel, target].sort() : [sentinel];
  const actualValue = style.getPropertyValue(target);
  assert_array_equals([
    present && value === "" ? actualValue.trim() : actualValue,
    JSON.stringify(names),
    style.length - getComputedStyle(reference).length
  ], [value, JSON.stringify(expected), expected.length], "Value, indexed names and length delta");
}

const cases = [
  ["20px", "initial", "", false, "Inherited value reset to initial"],
  ["20px", "var(--enumeration-missing)", "", false, "Inherited value replaced by missing variable"],
  ["20px", "var(--enumeration-target)", "", false, "Inherited value replaced by self cycle"],
  [null, "initial", "", false, "Initial without parent value"],
  [null, "var(--enumeration-missing)", "", false, "Missing variable without parent value"],
  ["20px", "var(--enumeration-missing,)", "", true, "Valid empty value remains enumerable"],
  ["20px", "inherit", "20px", true, "Inherited present value remains enumerable"]
];
for (const [parentValue, specified, value, present, name] of cases) {
  test(t => {
    const { child, reference } = fixture(t, parentValue);
    child.style.setProperty(target, specified);
    check(child, reference, value, present);
  }, name);
}

test(t => {
  const { child, reference } = fixture(t, "20px");
  check(child, reference, "20px", true);
  child.style.setProperty(target, "initial");
  check(child, reference, "", false);
  child.style.removeProperty(target);
  check(child, reference, "20px", true);
}, "Present to guaranteed-invalid to inherited present");

test(t => {
  const parent = document.createElement("div");
  const child = document.createElement("div");
  const reference = document.createElement("div");
  const name = "--last-enumerated-value";
  parent.style.setProperty(name, "10px");
  parent.append(child);
  document.body.append(parent, reference);
  t.add_cleanup(() => { parent.remove(); reference.remove(); });
  const style = getComputedStyle(child);
  function checkLast(expectedNames, expectedValue) {
    assert_array_equals(Array.from(style).filter(name => name.startsWith("--")), expectedNames);
    assert_equals(style.length - getComputedStyle(reference).length, expectedNames.length);
    const actualValue = style.getPropertyValue(name);
    assert_equals(expectedNames.length && expectedValue === "" ? actualValue.trim() : actualValue, expectedValue);
  }
  checkLast([name], "10px");
  child.style.setProperty(name, "initial");
  checkLast([], "");
  child.style.removeProperty(name);
  checkLast([name], "10px");
  child.style.setProperty(name, "initial");
  checkLast([], "");
  child.style.setProperty(name, "var(--last-missing,)");
  checkLast([name], "");
}, "Removing and restoring the last custom property updates a live computed style");

test(t => {
  const inherited = "--enumerated-inherited-value";
  const reset = "--enumerated-reset-value";
  CSS.registerProperty({name: reset, syntax: "*", inherits: false});
  const parent = document.createElement("div");
  const child = document.createElement("div");
  const reference = document.createElement("div");
  parent.style.setProperty(inherited, "10px");
  child.style.setProperty(reset, "20px");
  parent.append(child);
  document.body.append(parent, reference);
  t.add_cleanup(() => { parent.remove(); reference.remove(); });
  const style = getComputedStyle(child);
  function checkMaps(expectedNames, inheritedValue, resetValue) {
    assert_array_equals(Array.from(style).filter(name => name.startsWith("--")).sort(), expectedNames.sort());
    assert_equals(style.length - getComputedStyle(reference).length, expectedNames.length);
    assert_equals(style.getPropertyValue(inherited), inheritedValue);
    assert_equals(style.getPropertyValue(reset), resetValue);
  }
  checkMaps([inherited, reset], "10px", "20px");
  child.style.setProperty(inherited, "initial");
  checkMaps([reset], "", "20px");
  child.style.setProperty(reset, "var(--enumerated-missing)");
  checkMaps([], "", "");
  child.style.setProperty(reset, "30px");
  checkMaps([reset], "", "30px");
  child.style.removeProperty(inherited);
  checkMaps([inherited, reset], "10px", "30px");
}, "Enumeration crosses inherited and non-inherited maps after values become invalid");
