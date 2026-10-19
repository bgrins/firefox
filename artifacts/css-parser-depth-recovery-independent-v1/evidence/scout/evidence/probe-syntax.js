
function colorFor(t, declarations, mode) {
  const target = document.createElement("div");
  target.id = "target";
  document.body.append(target);
  t.add_cleanup(() => target.remove());
  if (mode === "inline") {
    target.style.cssText = declarations;
  } else {
    const style = document.createElement("style");
    style.textContent = `#target { ${declarations} }`;
    document.head.append(style);
    t.add_cleanup(() => style.remove());
  }
  return getComputedStyle(target).color;
}

for (const mode of ["inline", "stylesheet"]) {
  for (const depth of [1, 74, 75, 76]) {
    test(t => {
      const value = "calc(".repeat(depth) + "1px" +
        ")".repeat(depth - 1) + ";color:blue;)";
      assert_equals(colorFor(t, `color:red;width:${value}`, mode),
                    "rgb(255, 0, 0)");
    }, `${mode}: semicolon inside ${depth} nested functions stays in the value`);
  }
  test(t => {
    assert_equals(colorFor(t, "color:red;width:calc(1px);color:blue", mode),
                  "rgb(0, 0, 255)");
  }, `${mode}: a declaration outside the function applies`);
}
