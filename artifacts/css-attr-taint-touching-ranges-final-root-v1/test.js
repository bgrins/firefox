
const image = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
const quoted = JSON.stringify(image);
let counter = 0;
function setup(t) {
  const element = document.createElement("div");
  const reference = document.createElement("div");
  document.body.append(element, reference);
  t.add_cleanup(() => { element.remove(); reference.remove(); });
  const name = `--touch-density-${counter++}`;
  CSS.registerProperty({name, syntax: "<resolution>", inherits: false, initialValue: "2x"});
  element.setAttribute("data-density", "1x");
  element.setAttribute("data-image", image);
  element.style.setProperty(name, "attr(data-density type(<resolution>))");
  reference.style.setProperty(name, "1x");
  assert_equals(getComputedStyle(element).getPropertyValue(name),
                getComputedStyle(reference).getPropertyValue(name),
                "Typed resolution attr() computes the distinct 1x value");
  const literal = `image-set(${quoted}1x)`;
  assert_true(CSS.supports("background-image", literal), "Adjacent string and resolution grammar is supported");
  reference.style.backgroundImage = literal;
  const expected = getComputedStyle(reference).backgroundImage;
  assert_not_equals(expected, "none", "Literal URL calibration");
  return {element, expected};
}
for (const [name, value, blocked] of [
  ["Touching untainted URL and attr resolution", `image-set(${quoted}attr(data-density type(<resolution>)))`, false],
  ["Touching URL function and attr resolution", `image-set(url(${quoted})attr(data-density type(<resolution>)))`, false],
  ["Separated untainted URL and attr resolution", `image-set(${quoted} attr(data-density type(<resolution>)))`, false],
  ["Literal adjacent URL and resolution", `image-set(${quoted}1x)`, false],
  ["Attribute URL remains tainted", "image-set(attr(data-image) 1x)", true],
  ["Whole custom property substitution remains tainted", "var(--whole-image)", true],
  ["Later attribute URL remains tainted", `image-set(${quoted}attr(data-density type(<resolution>)), attr(data-image) 2x)`, true],
]) {
  test(t => {
    const {element, expected} = setup(t);
    element.style.setProperty("--whole-image", `image-set(${quoted} attr(data-density type(<resolution>)))`);
    element.style.backgroundImage = value;
    assert_not_equals(element.style.backgroundImage, "", "Declaration accepted before substitution");
    assert_equals(getComputedStyle(element).backgroundImage, blocked ? "none" : expected);
  }, name);
}
